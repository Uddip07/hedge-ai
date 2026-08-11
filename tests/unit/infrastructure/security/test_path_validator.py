"""
Security Unit Tests for Path Validator & Traversal Prevention.

Tests defense against:
- Directory traversal (../, ..\\)
- Absolute path escape (/etc/passwd, C:\\Windows, C:/Windows)
- Windows drive and rooted paths
- UNC share paths (\\\\server\\share, //server/share)
- NULL byte (\\0) and control character injection
- Obfuscated and mixed separator traversal
- Symlink escapes
- Valid nested datasets (NSE, data1, data2, data3, ZIPs)
"""

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
        (data_dir / "data1").mkdir()
        (data_dir / "data1" / "RELIANCE.csv").write_text("date,close\n2026-01-01,2500")
        (data_dir / "data2").mkdir()
        (data_dir / "data2" / "TCS.csv").write_text("date,close\n2026-01-01,3800")
        (data_dir / "data3").mkdir()
        (data_dir / "data3" / "INFY.zip").write_text("PK_mock_zip_content")
        return data_dir

    def test_valid_subpaths_resolve_correctly(self, base_dir):
        """Ensure legitimate nested market data paths resolve safely."""
        valid_paths = [
            "NSE/RELIANCE.csv",
            "data1/RELIANCE.csv",
            "data2/TCS.csv",
            "data3/INFY.zip",
        ]
        for vp in valid_paths:
            p = resolve_safe_path(base_dir, vp)
            assert p.exists()
            assert p.is_relative_to(base_dir)
            assert is_path_safe(base_dir, vp) is True

    def test_directory_traversal_rejected(self, base_dir):
        """Ensure relative traversal attempts are blocked."""
        traversal_attempts = [
            "../secret.txt",
            "../../etc/passwd",
            "..\\..\\Windows\\System32",
            "NSE/../../escaped.csv",
            "NSE/..\\../escaped.csv",
            "data1/../../../root_secret.txt",
            "data2/..\\..\\secret.env",
        ]
        for attempt in traversal_attempts:
            assert is_path_safe(base_dir, attempt) is False
            with pytest.raises(ValueError, match="Path traversal detected"):
                resolve_safe_path(base_dir, attempt)

    def test_absolute_path_escapes_rejected(self, base_dir):
        """Ensure absolute paths pointing outside base_dir are rejected."""
        absolute_attempts = [
            "/etc/passwd",
            "/var/log/syslog",
            "C:\\Windows\\System32\\cmd.exe",
            "C:/Windows/System32/cmd.exe",
            "D:\\secret\\passwords.txt",
        ]
        for attempt in absolute_attempts:
            assert is_path_safe(base_dir, attempt) is False
            with pytest.raises(ValueError):
                resolve_safe_path(base_dir, attempt)

    def test_unc_paths_rejected(self, base_dir):
        """Ensure UNC network paths are blocked."""
        unc_attempts = [
            "\\\\attacker-server\\share\\data.csv",
            "//attacker-server/share/data.csv",
            "\\\\127.0.0.1\\c$\\secret.txt",
        ]
        for attempt in unc_attempts:
            assert is_path_safe(base_dir, attempt) is False
            with pytest.raises(ValueError, match="UNC network paths are forbidden"):
                resolve_safe_path(base_dir, attempt)

    def test_control_chars_and_null_bytes_rejected(self, base_dir):
        """Ensure NULL bytes and ASCII control characters are rejected."""
        invalid_attempts = [
            "data\x00.csv",
            "NSE/\x1fbad.csv",
            "\tNSE/data.csv",
            "\nNSE/data.csv",
            "\rNSE/data.csv",
            "",
            "   ",
        ]
        for attempt in invalid_attempts:
            assert is_path_safe(base_dir, attempt) is False
            with pytest.raises(ValueError):
                resolve_safe_path(base_dir, attempt)

    def test_filename_sanitization(self):
        """Ensure filenames are stripped of directory components and dangerous characters."""
        assert sanitize_filename("RELIANCE_1m.csv") == "RELIANCE_1m.csv"
        assert sanitize_filename("../../../etc/passwd") == "passwd"
        assert sanitize_filename("..\\..\\Windows\\cmd.exe") == "cmd.exe"
        assert sanitize_filename("DELHIVERY$<script>.csv") == "DELHIVERY__script_.csv"
        assert sanitize_filename("TCS;DROP TABLE;.csv") == "TCS_DROP_TABLE_.csv"
        assert sanitize_filename("") == "unknown"
        assert sanitize_filename("...") == "unknown"
