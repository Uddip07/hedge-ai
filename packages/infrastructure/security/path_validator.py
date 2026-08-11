"""
Filesystem Path Traversal and Injection Security Module.

Enforces strict path normalization, base-directory containment, and defense against:
- Directory traversal (../, ..\\)
- Absolute path escape (/etc/passwd, C:\\Windows)
- UNC share paths (\\\\server\\share)
- NULL byte (\\0) and control character injection
- Obfuscated and mixed separator traversal across POSIX and Windows platforms
"""

import os
import re
from pathlib import Path


def is_path_safe(base_dir: str | Path, untrusted_path: str | Path) -> bool:
    """
    Check if a path safely resolves strictly within the intended base directory.
    """
    try:
        resolve_safe_path(base_dir, untrusted_path)
        return True
    except (ValueError, TypeError):
        return False


def resolve_safe_path(base_dir: str | Path, untrusted_path: str | Path) -> Path:
    """
    Safely resolve a target path relative to an intended base directory.

    Guarantees that the resolved path is located strictly within base_dir.
    Rejects directory traversal attempts, absolute path escapes, UNC paths,
    and control characters across both POSIX and Windows systems.

    Args:
        base_dir: The trusted base directory.
        untrusted_path: The untrusted subpath or filename to resolve.

    Returns:
        Path: The securely resolved absolute Path object.

    Raises:
        ValueError: If untrusted_path escapes base_dir or contains malicious characters.
    """
    if untrusted_path is None:
        raise ValueError("Target path cannot be None.")

    raw_str = str(untrusted_path)

    # Reject empty paths or paths with NULL bytes / control characters / tabs / newlines
    if any(ord(c) < 32 or ord(c) == 127 for c in raw_str):
        raise ValueError("Target path contains illegal control characters or whitespace.")

    str_path = raw_str.strip()
    if not str_path:
        raise ValueError("Target path cannot be empty.")

    # Reject UNC paths (\\server\share or //server/share)
    if str_path.startswith(("\\\\", "//")):
        raise ValueError("UNC network paths are forbidden.")

    # Resolve trusted base directory to absolute path
    resolved_base = Path(base_dir).resolve()

    # Normalize backslashes to forward slashes for robust cross-platform resolution
    normalized_path = str_path.replace("\\", "/")

    # Check for Windows drive letter specification (e.g. C: or C:/...)
    has_win_drive = bool(re.match(r"^[a-zA-Z]:", normalized_path))

    # Check for absolute path injection attempts
    raw_path_obj = Path(normalized_path)
    if raw_path_obj.is_absolute() or raw_path_obj.drive or normalized_path.startswith("/"):
        candidate = raw_path_obj.resolve()
    elif has_win_drive:
        if resolved_base.drive:
            candidate = Path(str_path).resolve()
        else:
            # On POSIX systems, a Windows drive path cannot be inside a POSIX base_dir
            raise ValueError(
                f"Path traversal detected: '{str_path}' is an absolute Windows drive path outside '{resolved_base}'."
            )
    else:
        candidate = (resolved_base / normalized_path).resolve()

    # Verify candidate is contained strictly within base_dir
    try:
        if not candidate.is_relative_to(resolved_base):
            raise ValueError(
                f"Path traversal detected: '{str_path}' resolves outside '{resolved_base}'."
            )
    except AttributeError:
        common = os.path.commonpath([str(resolved_base), str(candidate)])
        if common != str(resolved_base):
            raise ValueError(
                f"Path traversal detected: '{str_path}' resolves outside '{resolved_base}'."
            ) from None

    return candidate


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to allow only alphanumeric characters, dashes, underscores, and dots.
    Extracts base filename and prevents path traversal via filename parameters across POSIX and Windows.
    """
    if not filename:
        return "unknown"

    # Normalize backslashes to forward slashes first to handle Windows paths on POSIX runners
    normalized = str(filename).replace("\\", "/")
    # Extract base name to drop any directory components
    base_name = Path(normalized).name
    clean = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", base_name)
    # Remove leading dots or underscores that could create hidden files or traversal artifacts
    clean = clean.lstrip("._")
    if not clean:
        clean = "unknown"
    return clean
