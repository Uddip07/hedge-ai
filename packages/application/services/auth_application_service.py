"""
Authentication Application Service.
"""

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from packages.domain.enums.portfolio import PortfolioType
from packages.domain.enums.system import CurrencyCode, UserRole
from packages.domain.exceptions.business import (
    InvalidCredentialsError,
    InvalidTokenError,
    UnauthorizedError,
    UserAlreadyExistsError,
)
from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.repositories.portfolio_repository import PortfolioRepository
from packages.domain.repositories.user_repository import UserRepository
from packages.domain.user.session import UserSession
from packages.domain.user.user import User, UserPreferences, UserSettings
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.identifiers.currency import Currency
from packages.domain.value_objects.identifiers.uuid_wrappers import UserId
from packages.domain.value_objects.temporal.timestamps import Timestamp
from packages.infrastructure.security.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class AuthApplicationService:
    """
    Application Service orchestrating signup, login, session validation, logout, and profile management.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        portfolio_repository: PortfolioRepository,
    ) -> None:
        self.user_repo = user_repository
        self.portfolio_repo = portfolio_repository

    def signup(
        self,
        email: str,
        password: str,
        full_name: str,
        role: UserRole = UserRole.USER,
    ) -> dict[str, Any]:
        """
        Register new user, create paper trading account, and return user profile payload.
        """
        norm_email = User.normalize_email(email)
        existing = self.user_repo.get_by_email(norm_email)
        if existing:
            raise UserAlreadyExistsError(f"User with email '{norm_email}' already exists.")

        User.validate_password_strength(password)
        pwd_hash = hash_password(password)

        user_id = UserId.generate()
        account_name = f"{full_name.strip()}'s Paper Trading Account"
        paper_portfolio = Portfolio(
            name=account_name,
            portfolio_type=PortfolioType.PAPER,
            owner_id=user_id.value,
        )
        paper_portfolio.deposit_cash(
            Money(Decimal("1000000.00"), currency=Currency(CurrencyCode.INR))
        )
        self.portfolio_repo.save(paper_portfolio)

        self.portfolio_repo.save(paper_portfolio)

        user = User(
            id=user_id,
            email=norm_email,
            password_hash=pwd_hash,
            full_name=full_name.strip(),
            role=role,
            paper_portfolio_id=paper_portfolio.id,
        )
        self.user_repo.save(user)
        return user.to_dict()

    def login(
        self,
        email: str,
        password: str,
        user_agent: str = "",
        ip_address: str = "",
    ) -> dict[str, Any]:
        """
        Authenticate user credentials, generate session and JWT token pair.
        """
        user = self.user_repo.get_by_email(email)
        if not user or not user.is_active:
            raise InvalidCredentialsError("Invalid email or password.")

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password.")

        session_id = uuid.uuid4()
        access_token = create_access_token(user_id=str(user.id), role=user.role.value)
        refresh_token = create_refresh_token(user_id=str(user.id), session_id=str(session_id))

        token_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
        expires_at = Timestamp(datetime.now(UTC) + timedelta(days=7))

        user_session = UserSession(
            id=session_id,
            user_id=user.id,
            refresh_token_hash=token_hash,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at,
        )
        self.user_repo.save_session(user_session)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900,
            "user": user.to_dict(),
        }

    def refresh(self, refresh_token_str: str) -> dict[str, Any]:
        """
        Validate refresh token and issue new access token.
        """
        payload = decode_token(refresh_token_str)
        if payload.get("type") != "refresh":
            raise InvalidTokenError("Provided token is not a refresh token.")

        user_id_str = payload.get("sub")
        session_id_str = payload.get("sid")
        if not user_id_str or not session_id_str:
            raise InvalidTokenError("Refresh token payload missing claims.")

        session = self.user_repo.get_session(session_id_str)
        if not session or not session.is_valid:
            raise UnauthorizedError("Session is revoked or expired.")

        token_hash = hashlib.sha256(refresh_token_str.encode("utf-8")).hexdigest()
        if session.refresh_token_hash != token_hash:
            raise InvalidTokenError("Refresh token hash mismatch.")

        user = self.user_repo.get_by_id(UserId.from_str(user_id_str))
        if not user or not user.is_active:
            raise UnauthorizedError("User account disabled or not found.")

        new_access_token = create_access_token(user_id=str(user.id), role=user.role.value)
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 900,
        }

    def logout(self, user_id: UserId, session_id: str | None = None) -> None:
        """
        Revoke active user sessions.
        """
        if session_id:
            sess = self.user_repo.get_session(session_id)
            if sess:
                sess.revoke()
                self.user_repo.save_session(sess)
        else:
            self.user_repo.revoke_all_user_sessions(user_id)

    def get_user_profile(self, user_id: UserId) -> User:
        """Fetch user profile aggregate."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedError("User profile not found.")
        return user

    def update_user_profile(self, user_id: UserId, full_name: str | None = None) -> User:
        """Update user profile metadata."""
        user = self.get_user_profile(user_id)
        user.update_profile(full_name=full_name)
        self.user_repo.save(user)
        return user

    def add_watchlist(self, user_id: UserId, symbol: str) -> User:
        """Add ticker symbol to user watchlist."""
        user = self.get_user_profile(user_id)
        user.add_to_watchlist(symbol)
        self.user_repo.save(user)
        return user

    def remove_watchlist(self, user_id: UserId, symbol: str) -> User:
        """Remove ticker symbol from user watchlist."""
        user = self.get_user_profile(user_id)
        user.remove_from_watchlist(symbol)
        self.user_repo.save(user)
        return user

    def update_preferences(self, user_id: UserId, pref_dict: dict[str, Any]) -> User:
        """Update user domain preferences."""
        user = self.get_user_profile(user_id)
        user.preferences = UserPreferences.from_dict({**user.preferences.to_dict(), **pref_dict})
        user._touch()
        self.user_repo.save(user)
        return user

    def update_settings(self, user_id: UserId, settings_dict: dict[str, Any]) -> User:
        """Update user operational settings."""
        user = self.get_user_profile(user_id)
        user.settings = UserSettings.from_dict({**user.settings.to_dict(), **settings_dict})
        user._touch()
        self.user_repo.save(user)
        return user
