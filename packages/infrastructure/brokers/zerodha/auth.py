"""
Zerodha OAuth Authentication and Token Storage Module.

Provides TokenStore interface, FileTokenStore implementation, and ZerodhaAuthenticator
using the official kiteconnect Python SDK.
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, cast

try:
    from kiteconnect import KiteConnect
except ImportError:

    class KiteConnect:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def set_access_token(self, token: str) -> None:
            pass

        def login_url(self) -> str:
            return "https://kite.zerodha.com/connect/login"

        def generate_session(self, request_token: str, api_secret: str) -> dict[str, Any]:
            return {"access_token": "mock_token", "user_id": "mock_user"}

        def profile(self) -> dict[str, Any]:
            return {"user_id": "mock_user"}


logger = logging.getLogger("ihf_ai.infrastructure.brokers.zerodha.auth")


class TokenStore(ABC):
    """Abstract Interface for secure Access Token storage."""

    @abstractmethod
    def save_token(self, token: str, metadata: dict[str, Any] | None = None) -> None:
        """Persist access token securely."""

    @abstractmethod
    def get_token(self) -> str | None:
        """Retrieve stored access token if available."""

    @abstractmethod
    def get_metadata(self) -> dict[str, Any]:
        """Retrieve associated token metadata if available."""

    @abstractmethod
    def clear_token(self) -> None:
        """Clear stored token."""


class FileTokenStore(TokenStore):
    """File-based TokenStore implementation for local development."""

    def __init__(self, file_path: str | Path | None = None) -> None:
        if file_path:
            self.file_path = Path(file_path)
        else:
            env_path = os.getenv("ZERODHA_TOKEN_STORE_PATH")
            self.file_path = (
                Path(env_path) if env_path else Path.home() / ".moneyyyyyy" / "zerodha_session.json"
            )

    def save_token(self, token: str, metadata: dict[str, Any] | None = None) -> None:
        """Save access_token and session metadata securely to disk."""
        data = {
            "access_token": token,
            "metadata": metadata or {},
        }
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info("Access token successfully stored in FileTokenStore at %s", self.file_path)
        except OSError as exc:
            logger.error("Failed to write token store to %s: %s", self.file_path, str(exc))

    def get_token(self) -> str | None:
        """Read access_token from disk."""
        if not self.file_path.exists():
            return None
        try:
            with open(self.file_path, encoding="utf-8") as f:
                data = json.load(f)
                return cast(str | None, data.get("access_token"))
        except Exception as exc:
            logger.error("Failed to read token store from %s: %s", self.file_path, str(exc))
            return None

    def get_metadata(self) -> dict[str, Any]:
        """Read metadata payload from disk."""
        if not self.file_path.exists():
            return {}
        try:
            with open(self.file_path, encoding="utf-8") as f:
                data = json.load(f)
                return cast(dict[str, Any], data.get("metadata", {}))
        except Exception:
            return {}

    def clear_token(self) -> None:
        """Remove cached token file from disk."""
        if self.file_path.exists():
            try:
                self.file_path.unlink()
                logger.info("Cleared token file at %s", self.file_path)
            except OSError as exc:
                logger.error("Error removing token file: %s", str(exc))


class ZerodhaAuthenticator:
    """
    Manages Zerodha KiteConnect OAuth authentication flow.
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        redirect_uri: str | None = None,
        token_store: TokenStore | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("ZERODHA_API_KEY", "")
        self.api_secret = api_secret or os.getenv("ZERODHA_API_SECRET", "")
        self.redirect_uri = (
            redirect_uri
            or os.getenv("ZERODHA_REDIRECT_URI")
            or os.getenv("ZERODHA_REDIRECT_URL")
            or "http://localhost:8000/auth/zerodha/callback"
        )
        self.token_store = token_store or FileTokenStore()
        self.kite = KiteConnect(api_key=self.api_key)

        # Load existing access token if available
        cached_token = self.token_store.get_token() or os.getenv("ZERODHA_ACCESS_TOKEN")
        if cached_token:
            self.kite.set_access_token(cached_token)

    def get_login_url(self) -> str:
        """Return official Zerodha OAuth login URL."""
        if not self.api_key:
            raise ValueError("ZERODHA_API_KEY is not set.")
        return str(self.kite.login_url())

    def generate_session(self, request_token: str) -> dict[str, Any]:
        """
        Exchange request_token for access_token using official KiteConnect SDK.
        """
        if not self.api_key or not self.api_secret:
            raise ValueError("ZERODHA_API_KEY and ZERODHA_API_SECRET must be set for auth.")

        try:
            data = self.kite.generate_session(
                request_token=request_token,
                api_secret=self.api_secret,
            )
            access_token = data.get("access_token")
            if not access_token:
                raise ValueError(
                    "Zerodha session generation response did not contain access_token."
                )

            self.kite.set_access_token(access_token)
            self.token_store.save_token(access_token, metadata=data)
            logger.info("Successfully authenticated Zerodha user %s", data.get("user_id"))
            return cast(dict[str, Any], data if isinstance(data, dict) else {})
        except Exception as exc:
            logger.error("Failed Zerodha OAuth session generation: %s", str(exc))
            raise

    def get_active_access_token(self) -> str | None:
        """Return active access token from TokenStore or environment."""
        return self.token_store.get_token() or os.getenv("ZERODHA_ACCESS_TOKEN")

    def is_authenticated(self) -> bool:
        """Check if access token is configured and valid."""
        token = self.get_active_access_token()
        if not token:
            return False
        try:
            profile = self.kite.profile()
            return bool(profile and profile.get("user_id"))
        except Exception:
            return False
