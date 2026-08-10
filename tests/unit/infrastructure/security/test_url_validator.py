"""
Security Unit Tests for URL Validator & Sanitizer.

Tests defense against:
- Hostname substring spoofing (e.g. attacker.com?param=kite.zerodha.com)
- Subdomain injection (e.g. kite.zerodha.com.attacker.com)
- Scheme injection (e.g. javascript:, data:, file:)
- CRLF and control character injection
- Userinfo tricks (e.g. https://user:pass@kite.zerodha.com)
"""

import pytest

from packages.infrastructure.security.url_validator import (
    is_safe_zerodha_url,
    validate_zerodha_url,
)


class TestURLValidatorSecurity:
    """Test URL security and adversarial bypass prevention."""

    def test_valid_zerodha_urls_accepted(self):
        valid_urls = [
            "https://kite.zerodha.com/connect/login?api_key=xyz&v=3",
            "https://kite.trade/connect/login?api_key=xyz",
            "https://api.kite.trade/orders",
            "http://localhost:8000/auth/zerodha/callback",
            "http://127.0.0.1:8000/auth/zerodha/callback",
        ]
        for url in valid_urls:
            assert is_safe_zerodha_url(url) is True
            assert validate_zerodha_url(url) == url

    def test_malicious_subdomain_spoofing_rejected(self):
        spoofed_urls = [
            "https://kite.zerodha.com.evil.com/login",
            "https://evil-kite.zerodha.com/login",
            "https://kite.zerodha.com.attacker.org",
            "https://sub.kite.trade.attacker.org",
        ]
        for url in spoofed_urls:
            assert is_safe_zerodha_url(url) is False
            with pytest.raises(ValueError, match="Invalid or untrusted Zerodha URL"):
                validate_zerodha_url(url)

    def test_query_parameter_hostname_injection_rejected(self):
        injected_urls = [
            "https://evil.com/?target=kite.zerodha.com",
            "https://evil.com/redirect?url=https://kite.zerodha.com",
            "https://attacker.org#kite.zerodha.com",
        ]
        for url in injected_urls:
            assert is_safe_zerodha_url(url) is False
            with pytest.raises(ValueError):
                validate_zerodha_url(url)

    def test_dangerous_schemes_rejected(self):
        dangerous_urls = [
            "javascript:alert(document.cookie)",
            "data:text/html,<script>alert(1)</script>",
            "file:///etc/passwd",
            "ftp://kite.zerodha.com/exploit",
            "vbscript:msgbox(1)",
        ]
        for url in dangerous_urls:
            assert is_safe_zerodha_url(url) is False
            with pytest.raises(ValueError):
                validate_zerodha_url(url)

    def test_userinfo_injection_rejected(self):
        userinfo_urls = [
            "https://attacker:secret@kite.zerodha.com/login",
            "https://user@kite.trade",
        ]
        for url in userinfo_urls:
            assert is_safe_zerodha_url(url) is False
            with pytest.raises(ValueError):
                validate_zerodha_url(url)

    def test_crlf_and_control_chars_rejected(self):
        malformed_urls = [
            "https://kite.zerodha.com\r\nSet-Cookie: admin=true",
            "https://kite.zerodha.com\x00/evil",
            "https://kite.zerodha.com\t/path",
        ]
        for url in malformed_urls:
            assert is_safe_zerodha_url(url) is False
            with pytest.raises(ValueError):
                validate_zerodha_url(url)
