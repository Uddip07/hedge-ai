"""
SQLAlchemy Implementation of UserRepository.
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select, update

from packages.domain.enums.system import UserRole
from packages.domain.repositories.user_repository import UserRepository
from packages.domain.user.session import UserSession
from packages.domain.user.user import User, UserPreferences, UserSettings
from packages.domain.value_objects.identifiers.uuid_wrappers import PortfolioId, UserId
from packages.domain.value_objects.temporal.timestamps import Timestamp
from packages.infrastructure.database.models import UserModel, UserSessionModel
from packages.infrastructure.repositories.base_sql_repository import BaseSQLRepository


class SQLUserRepository(BaseSQLRepository[User, UserId], UserRepository):
    """
    SQLAlchemy 2.x Repository for User Aggregate Root.
    Fallback to in-memory store if session_factory is None.
    """

    def __init__(self, session_factory: Any = None) -> None:
        super().__init__(session_factory)
        self._in_memory_sessions: dict[str, UserSession] = {}

    def _to_domain(self, model: UserModel) -> User:
        paper_id = (
            PortfolioId.from_str(model.paper_portfolio_id) if model.paper_portfolio_id else None
        )
        return User(
            id=UserId.from_str(model.id),
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            role=UserRole(model.role),
            is_active=model.is_active,
            paper_portfolio_id=paper_id,
            watchlist=list(model.watchlist or []),
            research_history=list(model.research_history or []),
            committee_history=list(model.committee_history or []),
            preferences=UserPreferences.from_dict(model.preferences or {}),
            settings=UserSettings.from_dict(model.settings or {}),
            created_at=Timestamp.from_iso(
                model.created_at.isoformat()
                if isinstance(model.created_at, datetime)
                else str(model.created_at)
            ),
            updated_at=Timestamp.from_iso(
                model.updated_at.isoformat()
                if isinstance(model.updated_at, datetime)
                else str(model.updated_at)
            ),
        )

    def _session_to_domain(self, model: UserSessionModel) -> UserSession:
        return UserSession(
            id=uuid.UUID(model.id),
            user_id=UserId.from_str(model.user_id),
            refresh_token_hash=model.refresh_token_hash,
            user_agent=model.user_agent,
            ip_address=model.ip_address,
            is_revoked=model.is_revoked,
            expires_at=Timestamp.from_iso(
                model.expires_at.isoformat()
                if isinstance(model.expires_at, datetime)
                else str(model.expires_at)
            ),
            created_at=Timestamp.from_iso(
                model.created_at.isoformat()
                if isinstance(model.created_at, datetime)
                else str(model.created_at)
            ),
        )

    def get_by_id(self, user_id: UserId) -> User | None:
        key_str = str(user_id)
        if self.session_factory is None:
            return self._in_memory_store.get(key_str)

        with self.session_factory() as session:
            stmt = select(UserModel).where(UserModel.id == key_str)
            model = session.scalar(stmt)
            return self._to_domain(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        norm_email = email.strip().lower()
        if self.session_factory is None:
            return next((u for u in self._in_memory_store.values() if u.email == norm_email), None)

        with self.session_factory() as session:
            stmt = select(UserModel).where(UserModel.email == norm_email)
            model = session.scalar(stmt)
            return self._to_domain(model) if model else None

    def list_all(self) -> list[User]:
        if self.session_factory is None:
            return list(self._in_memory_store.values())

        with self.session_factory() as session:
            stmt = select(UserModel)
            models = session.scalars(stmt).all()
            return [self._to_domain(m) for m in models]

    def save(self, user: User) -> None:
        key_str = str(user.id)
        self._in_memory_store[key_str] = user

        if self.session_factory is None:
            return

        with self.session_factory() as session:
            model = session.get(UserModel, key_str)
            if not model:
                model = UserModel(id=key_str)
                session.add(model)

            model.email = user.email
            model.password_hash = user.password_hash
            model.full_name = user.full_name
            model.role = user.role.value
            model.is_active = user.is_active
            model.paper_portfolio_id = (
                str(user.paper_portfolio_id) if user.paper_portfolio_id else None
            )
            model.watchlist = user.watchlist
            model.research_history = user.research_history
            model.committee_history = user.committee_history
            model.preferences = user.preferences.to_dict()
            model.settings = user.settings.to_dict()
            model.updated_at = datetime.now(UTC)
            session.commit()

    def delete(self, user_id: UserId) -> None:
        key_str = str(user_id)
        self._in_memory_store.pop(key_str, None)

        if self.session_factory is None:
            return

        with self.session_factory() as session:
            model = session.get(UserModel, key_str)
            if model:
                session.delete(model)
                session.commit()

    def save_session(self, user_session: UserSession) -> None:
        sess_id_str = str(user_session.id)
        self._in_memory_sessions[sess_id_str] = user_session

        if self.session_factory is None:
            return

        with self.session_factory() as session:
            model = session.get(UserSessionModel, sess_id_str)
            if not model:
                model = UserSessionModel(id=sess_id_str)
                session.add(model)

            model.user_id = str(user_session.user_id)
            model.refresh_token_hash = user_session.refresh_token_hash
            model.user_agent = user_session.user_agent
            model.ip_address = user_session.ip_address
            model.is_revoked = user_session.is_revoked
            model.expires_at = user_session.expires_at.value
            session.commit()

    def get_session(self, session_id: str) -> UserSession | None:
        if self.session_factory is None:
            return self._in_memory_sessions.get(session_id)

        with self.session_factory() as session:
            model = session.get(UserSessionModel, session_id)
            return self._session_to_domain(model) if model else None

    def revoke_all_user_sessions(self, user_id: UserId) -> None:
        uid_str = str(user_id)
        for s in self._in_memory_sessions.values():
            if str(s.user_id) == uid_str:
                s.revoke()

        if self.session_factory is None:
            return

        with self.session_factory() as session:
            stmt = (
                update(UserSessionModel)
                .where(UserSessionModel.user_id == uid_str)
                .values(is_revoked=True)
            )
            session.execute(stmt)
            session.commit()
