"""
User Aggregate Root for the Indian AI Hedge Fund Platform.
"""

import re
from dataclasses import dataclass, field
from typing import Any

from packages.domain.enums.system import UserRole
from packages.domain.exceptions.business import PasswordValidationError
from packages.domain.exceptions.validation import ValidationError
from packages.domain.value_objects.identifiers.uuid_wrappers import PortfolioId, UserId
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass
class UserPreferences:
    """User UI/UX and domain preferences."""

    theme: str = "dark"
    default_currency: str = "INR"
    notifications_enabled: bool = True
    risk_tolerance: str = "MODERATE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "theme": self.theme,
            "default_currency": self.default_currency,
            "notifications_enabled": self.notifications_enabled,
            "risk_tolerance": self.risk_tolerance,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserPreferences":
        return cls(
            theme=data.get("theme", "dark"),
            default_currency=data.get("default_currency", "INR"),
            notifications_enabled=bool(data.get("notifications_enabled", True)),
            risk_tolerance=data.get("risk_tolerance", "MODERATE"),
        )


@dataclass
class UserSettings:
    """User security and system operational settings."""

    mfa_enabled: bool = False
    session_timeout_minutes: int = 60
    max_active_sessions: int = 5
    api_access_enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "mfa_enabled": self.mfa_enabled,
            "session_timeout_minutes": self.session_timeout_minutes,
            "max_active_sessions": self.max_active_sessions,
            "api_access_enabled": self.api_access_enabled,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserSettings":
        return cls(
            mfa_enabled=bool(data.get("mfa_enabled", False)),
            session_timeout_minutes=int(data.get("session_timeout_minutes", 60)),
            max_active_sessions=int(data.get("max_active_sessions", 5)),
            api_access_enabled=bool(data.get("api_access_enabled", True)),
        )


@dataclass
class User:
    """
    User Aggregate Root.

    Owns user identity, password hash, role, and domain references.
    """

    email: str
    password_hash: str
    full_name: str
    id: UserId = field(default_factory=UserId.generate)
    role: UserRole = UserRole.USER
    is_active: bool = True
    paper_portfolio_id: PortfolioId | None = None
    watchlist: list[str] = field(default_factory=list)
    research_history: list[str] = field(default_factory=list)
    committee_history: list[str] = field(default_factory=list)
    preferences: UserPreferences = field(default_factory=UserPreferences)
    settings: UserSettings = field(default_factory=UserSettings)
    created_at: Timestamp = field(default_factory=Timestamp.now_utc)
    updated_at: Timestamp = field(default_factory=Timestamp.now_utc)

    def __post_init__(self) -> None:
        self.email = self.normalize_email(self.email)
        if not self.email or "@" not in self.email:
            raise ValidationError(f"Invalid email address: '{self.email}'")
        if not self.full_name or not self.full_name.strip():
            raise ValidationError("Full name cannot be empty.")
        if not isinstance(self.role, UserRole):
            self.role = UserRole(self.role)

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def validate_password_strength(password: str) -> None:
        if len(password) < 8:
            raise PasswordValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            raise PasswordValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            raise PasswordValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", password):
            raise PasswordValidationError("Password must contain at least one digit.")

    def add_to_watchlist(self, symbol: str) -> None:
        sym = symbol.strip().upper()
        if sym and sym not in self.watchlist:
            self.watchlist.append(sym)
            self._touch()

    def remove_from_watchlist(self, symbol: str) -> None:
        sym = symbol.strip().upper()
        if sym in self.watchlist:
            self.watchlist.remove(sym)
            self._touch()

    def record_research_activity(self, research_id: str) -> None:
        if research_id not in self.research_history:
            self.research_history.insert(0, research_id)
            self._touch()

    def record_committee_activity(self, evaluation_id: str) -> None:
        if evaluation_id not in self.committee_history:
            self.committee_history.insert(0, evaluation_id)
            self._touch()

    def update_profile(self, full_name: str | None = None) -> None:
        if full_name and full_name.strip():
            self.full_name = full_name.strip()
            self._touch()

    def _touch(self) -> None:
        self.updated_at = Timestamp.now_utc()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "paper_portfolio_id": str(self.paper_portfolio_id) if self.paper_portfolio_id else None,
            "watchlist": self.watchlist,
            "research_history": self.research_history,
            "committee_history": self.committee_history,
            "preferences": self.preferences.to_dict(),
            "settings": self.settings.to_dict(),
            "created_at": self.created_at.iso_format,
            "updated_at": self.updated_at.iso_format,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":
        paper_id = (
            PortfolioId.from_str(data["paper_portfolio_id"])
            if data.get("paper_portfolio_id")
            else None
        )
        return cls(
            id=UserId.from_str(data["id"]),
            email=data["email"],
            password_hash=data.get("password_hash", ""),
            full_name=data["full_name"],
            role=UserRole(data.get("role", "USER")),
            is_active=bool(data.get("is_active", True)),
            paper_portfolio_id=paper_id,
            watchlist=list(data.get("watchlist", [])),
            research_history=list(data.get("research_history", [])),
            committee_history=list(data.get("committee_history", [])),
            preferences=UserPreferences.from_dict(data.get("preferences", {})),
            settings=UserSettings.from_dict(data.get("settings", {})),
            created_at=Timestamp.from_iso(data["created_at"]),
            updated_at=Timestamp.from_iso(data["updated_at"]),
        )
