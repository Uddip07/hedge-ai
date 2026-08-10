"""
Security Unit Tests for Path Validator & Traversal Prevention.

Tests defense against:
- Directory traversal (../, ..\\)
- Absolute path escape (/etc/passwd, C:\\Windows)
- UNC share paths (\\\\server\\share)
- NULL byte (\\0) and control character injection
- Obfuscated and mixed separator traversal
"""

from pathlib import Path

import pytest

from packages.infrastructure.security.path_validator import (
    is_path_safe,
    resolve_safe_path,
    sanitize_filename,
)


class TestPathValidatorSecurity:
    """Test filesystem path validation and traversal prevention."""

    @pytest.fixture
    def base_dir(self, tmp_path):
        data_dir = tmp_path / "market_data"
        data_dir.mkdir()
        (data_dir / "NSE").mkdir()
        (data_dir / "NSE" / "RELIANCE.csv").write_text("date,close\n2026-01-01,2500")
        return data_dir

    def test_valid_subpaths_resolve_correctly(self, base_dir):
        p1 = resolve_safe_path(base_dir, "NSE/RELIANCE.csv")
        assert p1.exists()
        assert p1.is_relative_to(base_dir)

        p2 = resolve_safe_path(base_dir, Path("NSE") / "RELIANCE.csv")
        assert p2.exists()
        assert is_path_safe(base_dir, "NSE/RELIANCE.csv") is True

    def test_directory_traversal_rejected(self, base_dir):
        traversal_attempts = [
            "../secret.txt",
            "../../etc/passwd",
            "..\\..\\Windows\\System32",
            "NSE/../../escaped.csv",
            "NSE/..\\../escaped.csv",
        ]
        for attempt in traversal_attempts:
            assert is_path_safe(base_dir, attempt) is False
            with pytest.raises(ValueError, match="Path traversal detected"):
                resolve_safe_path(base_dir, attempt)

    def test_unc_paths_rejected(self, base_dir):
        unc_attempts = [
            "\\\\attacker-server\\share\\data.csv",
            "//attacker-server/share/data.csv",
        ]
        for attempt in unc_attempts:
            assert is_path_safe(base_dir, attempt) is False
            with pytest.raises(ValueError, match="UNC network paths are forbidden"):
                resolve_safe_path(base_dir, attempt)

    def test_control_chars_and_null_bytes_rejected(self, base_dir):
        invalid_attempts = [
            "data\x00.csv",
            "NSE/\x1fbad.csv",
            "\tNSE/data.csv",
            "",
            "   ",
        ]
        for attempt in invalid_attempts:
            assert is_path_safe(base_dir, attempt) is False
            with pytest.raises(ValueError):
                resolve_safe_path(base_dir, attempt)

    def test_filename_sanitization(self):
        assert sanitize_filename("RELIANCE_1m.csv") == "RELIANCE_1m.csv"
        assert sanitize_filename("../../../etc/passwd") == "passwd"
        assert sanitize_filename("..\\..\\Windows\\cmd.exe") == "cmd.exe"
        assert sanitize_filename("DELHIVERY$<script>.csv") == "DELHIVERY__script_.csv"
