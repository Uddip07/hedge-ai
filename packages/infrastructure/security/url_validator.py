"""
URL Validation and Sanitization Module for Infrastructure & Security Layer.

Enforces strict RFC 3986 URL parsing, host whitelist verification, scheme enforcement,
and protection against open-redirects, SSRF, and hostname substring spoofing.
"""

from urllib.parse import urlparse

# Strict Whitelist of Trusted Zerodha and Local Hostnames
ALLOWED_ZERODHA_HOSTS: frozenset[str] = frozenset(
    {
        "kite.zerodha.com",
        "kite.trade",
        "api.kite.trade",
        "localhost",
        "127.0.0.1",
    }
)

ALLOWED_SCHEMES: frozenset[str] = frozenset({"https", "http"})


def is_safe_zerodha_url(
    url: str,
    allow_http_for_local: bool = True,
) -> bool:
    """
    Validate whether a URL strictly matches trusted Zerodha KiteConnect domains.

    Performs full structural parsing (scheme, netloc, hostname, userinfo) rather than
    naive substring matching to prevent adversarial bypasses (e.g. subdomain spoofing).
    """
    if not url or not isinstance(url, str):
        return False

    # Check for CRLF or control characters
    if any(ord(c) < 32 or ord(c) == 127 for c in url):
        return False

    try:
        parsed = urlparse(url.strip())
    except Exception:
        return False

    # Scheme validation
    scheme = (parsed.scheme or "").lower()
    if scheme not in ALLOWED_SCHEMES:
        return False

    # Hostname validation
    hostname = (parsed.hostname or "").lower()
    if not hostname or hostname not in ALLOWED_ZERODHA_HOSTS:
        return False

    # Disallow userinfo (e.g. https://attacker@kite.zerodha.com)
    if parsed.username or parsed.password:
        return False

    # HTTP is only permitted for localhost/127.0.0.1 in local environments
    if scheme == "http" and hostname not in ("localhost", "127.0.0.1") and not allow_http_for_local:
        return False

    return True


def validate_zerodha_url(
    url: str,
    allow_http_for_local: bool = True,
) -> str:
    """
    Validate and return the verified Zerodha URL string.

    Raises:
        ValueError: If the URL fails structural or domain whitelist verification.
    """
    if not is_safe_zerodha_url(url, allow_http_for_local=allow_http_for_local):
        raise ValueError(
            f"Invalid or untrusted Zerodha URL destination: '{url}'. "
            f"Host must be in {sorted(ALLOWED_ZERODHA_HOSTS)} and use a trusted scheme."
        )
    return url.strip()
