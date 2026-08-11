"""
Market Data Auto-Discovery Scanner Engine.

Recursively scans the configured MARKET_DATA_PATH for folders, CSV files,
nested directories, and ZIP archives while filtering unsupported metadata files.
Zero hardcoding of folder names.
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from packages.infrastructure.database.config import DatabaseConfig
from packages.infrastructure.security.path_validator import sanitize_filename

IGNORED_PATTERNS = [
    r"^\._",
    r"^\.DS_Store",
    r"^__MACOSX",
    r"\.tmp$",
    r"\.bak$",
]


@dataclass
class DiscoveredFile:
    """
    Representation of a discovered data file.
    """

    file_path: Path
    relative_path: str
    folder_name: str
    file_type: str  # "csv" or "zip"
    estimated_symbol: str
    size_bytes: int


class DataScanner:
    """
    Recursive Auto-Discovery Scanner Engine for Market Data Directory.
    """

    def __init__(self, root_path: str | Path | None = None) -> None:
        if root_path is None:
            cfg = DatabaseConfig()
            root_path = cfg.market_data_path

        raw_str = str(root_path).strip()
        if not raw_str:
            raise ValueError("Scanner root_path cannot be empty.")
        if any(ord(c) < 32 or ord(c) == 127 for c in raw_str):
            raise ValueError("Scanner root_path contains illegal control characters.")
        if raw_str.startswith(("\\\\", "//")):
            raise ValueError("UNC network paths are forbidden for market data scanner.")

        self.root_path: Path = Path(raw_str).resolve()

    def is_ignored(self, path: Path | str) -> bool:
        """
        Check if a file or directory name should be ignored.
        """
        name = Path(path).name
        for pattern in IGNORED_PATTERNS:
            if re.search(pattern, name, re.IGNORECASE):
                return True
        return False

    def extract_symbol_from_name(self, filename: str) -> str:
        """
        Extract clean symbol ticker from filename.
        Examples:
          DELHIVERY_minute.csv -> DELHIVERY
          TRENT_minute.csv -> TRENT
          NIFTY_2022-05-02_1m.csv -> NIFTY
          RELIANCE.csv -> RELIANCE
        """
        clean_name = sanitize_filename(filename)
        stem = Path(clean_name).stem
        # Remove date/time suffixes or suffixes like _minute, _daily, _1m
        clean = re.sub(
            r"(_minute|_daily|_1m|_5m|_15m|_1h|_day|\d{4}-\d{2}-\d{2}.*)$",
            "",
            stem,
            flags=re.IGNORECASE,
        )
        clean = clean.split("_")[0].upper()
        return clean if clean else stem.upper()

    def scan_directories(self) -> list[Path]:
        """
        Detect all first-level subfolders inside root_path.
        """
        if not self.root_path.exists() or not self.root_path.is_dir():
            return []

        folders: list[Path] = []
        for entry in self.root_path.iterdir():
            if not entry.is_dir() or self.is_ignored(entry):
                continue

            # Ensure resolved entry stays strictly inside root_path (symlink protection)
            try:
                resolved_entry = entry.resolve()
                if not resolved_entry.is_relative_to(self.root_path):
                    continue
            except (ValueError, AttributeError):
                common = os.path.commonpath([str(self.root_path), str(entry.resolve())])
                if common != str(self.root_path):
                    continue

            folders.append(entry)
        return sorted(folders)

    def scan_files(self) -> list[DiscoveredFile]:
        """
        Recursively scan root_path for CSV files and Zip archives.
        """
        discovered: list[DiscoveredFile] = []

        if not self.root_path.exists() or not self.root_path.is_dir():
            return discovered

        # Scan filesystem files recursively with strict containment validation
        for path in self.root_path.rglob("*"):
            if not path.is_file() or self.is_ignored(path):
                continue

            # Ensure resolved path does not escape root_path (symlink escape protection)
            try:
                resolved_path = path.resolve()
                if not resolved_path.is_relative_to(self.root_path):
                    continue
            except (ValueError, AttributeError):
                common = os.path.commonpath([str(self.root_path), str(path.resolve())])
                if common != str(self.root_path):
                    continue

            suffix = path.suffix.lower()
            if suffix in [".csv", ".zip"]:
                # Determine top-level folder name relative to root
                try:
                    rel = path.relative_to(self.root_path)
                    top_folder = rel.parts[0] if len(rel.parts) > 1 else "root"
                except ValueError:
                    top_folder = "root"

                symbol = self.extract_symbol_from_name(path.name)
                try:
                    size = path.stat().st_size
                except OSError:
                    size = 0

                discovered.append(
                    DiscoveredFile(
                        file_path=path,
                        relative_path=str(rel),
                        folder_name=top_folder,
                        file_type=suffix[1:],
                        estimated_symbol=symbol,
                        size_bytes=size,
                    )
                )

        return discovered

    def get_summary(self) -> dict[str, Any]:
        """
        Return high-level statistics on detected folders and files.
        """
        folders = self.scan_directories()
        files = self.scan_files()
        csv_count = sum(1 for f in files if f.file_type == "csv")
        zip_count = sum(1 for f in files if f.file_type == "zip")
        total_size = sum(f.size_bytes for f in files)

        return {
            "root_path": str(self.root_path),
            "folder_count": len(folders),
            "folders_detected": [f.name for f in folders],
            "total_files": len(files),
            "csv_files_count": csv_count,
            "zip_files_count": zip_count,
            "total_size_bytes": total_size,
        }
