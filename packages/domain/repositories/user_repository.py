"""
User Repository Interface.
"""

from abc import ABC, abstractmethod

from packages.domain.user.session import UserSession
from packages.domain.user.user import User
from packages.domain.value_objects.identifiers.uuid_wrappers import UserId


class UserRepository(ABC):
    """Abstract Repository Interface for User Aggregate Root persistence."""

    @abstractmethod
    def get_by_id(self, user_id: UserId) -> User | None:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def list_all(self) -> list[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass

    @abstractmethod
    def delete(self, user_id: UserId) -> None:
        pass

    @abstractmethod
    def save_session(self, session: UserSession) -> None:
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> UserSession | None:
        pass

    @abstractmethod
    def revoke_all_user_sessions(self, user_id: UserId) -> None:
        pass
