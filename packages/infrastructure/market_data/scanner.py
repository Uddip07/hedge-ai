"""
Market Data Auto-Discovery Scanner Engine.

Recursively scans the configured MARKET_DATA_PATH for folders, CSV files,
nested directories, and ZIP archives while filtering unsupported metadata files.
Zero hardcoding of folder names.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from packages.infrastructure.security.path_validator import resolve_safe_path, sanitize_filename

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

    def __init__(self, root_path: str | Path) -> None:
        if root_path is None:
            raise ValueError("Scanner root_path cannot be None.")
        str_root = str(root_path).strip()
        if not str_root:
            raise ValueError("Scanner root_path cannot be empty.")
        if any(ord(c) < 32 or ord(c) == 127 for c in str_root):
            raise ValueError("Scanner root_path contains illegal control characters.")
        if str_root.startswith(("\\\\", "//")):
            raise ValueError("UNC network paths are forbidden for market data scanner.")
        self.root_path = Path(str_root).resolve()

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

        folders = []
        for entry in self.root_path.iterdir():
            # Validate each entry stays within root_path
            try:
                safe_entry = resolve_safe_path(self.root_path, entry)
            except ValueError:
                continue

            if safe_entry.is_dir() and not self.is_ignored(safe_entry):
                folders.append(safe_entry)
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
            try:
                safe_path = resolve_safe_path(self.root_path, path)
            except ValueError:
                continue

            if safe_path.is_file() and not self.is_ignored(safe_path):
                suffix = safe_path.suffix.lower()
                if suffix in [".csv", ".zip"]:
                    # Determine top-level folder name relative to root
                    try:
                        rel = safe_path.relative_to(self.root_path)
                        top_folder = rel.parts[0] if len(rel.parts) > 1 else "root"
                    except ValueError:
                        top_folder = "root"

                    symbol = self.extract_symbol_from_name(safe_path.name)
                    discovered.append(
                        DiscoveredFile(
                            file_path=safe_path,
                            relative_path=str(rel),
                            folder_name=top_folder,
                            file_type=suffix[1:],
                            estimated_symbol=symbol,
                            size_bytes=safe_path.stat().st_size,
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
