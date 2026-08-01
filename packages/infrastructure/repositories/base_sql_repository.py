"""
Base SQL Repository Abstraction for SQLAlchemy 2.x Infrastructure.

Provides BaseSQLRepository abstract generic foundation for database persistence, mapping, and session transaction boundaries.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

TDomain = TypeVar("TDomain")
TKey = TypeVar("TKey")


class BaseSQLRepository(ABC, Generic[TDomain, TKey]):
    """
    Abstract Base SQL Repository enforcing Clean Architecture domain repository contract.
    """

    def __init__(self, session_factory: Any = None) -> None:
        self.session_factory = session_factory
        self._in_memory_store: dict[str, TDomain] = {}

    @abstractmethod
    def get_by_id(self, key: TKey) -> TDomain | None:
        """Fetch domain entity by primary key identifier."""

    @abstractmethod
    def list_all(self) -> list[TDomain]:
        """List all stored domain entities."""

    @abstractmethod
    def save(self, entity: TDomain) -> None:
        """Persist or update domain entity."""

    @abstractmethod
    def delete(self, key: TKey) -> None:
        """Delete domain entity by primary key identifier."""
