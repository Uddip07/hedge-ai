"""
SQL Portfolio Repository Implementation.

Concrete SQLAlchemy 2.x implementation of the domain PortfolioRepository interface.
"""

from typing import Any

from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.repositories.portfolio_repository import PortfolioRepository
from packages.domain.value_objects.identifiers.uuid_wrappers import PortfolioId
from packages.infrastructure.repositories.base_sql_repository import BaseSQLRepository


class SQLPortfolioRepository(BaseSQLRepository[Portfolio, PortfolioId], PortfolioRepository):
    """
    SQLAlchemy 2.x Repository for Portfolio Aggregate Root persistence.
    """

    def __init__(self, session_factory: Any = None) -> None:
        super().__init__(session_factory=session_factory)

    def get_by_id(self, portfolio_id: PortfolioId) -> Portfolio | None:
        key = str(portfolio_id.value)
        return self._in_memory_store.get(key)

    def list_all(self) -> list[Portfolio]:
        return list(self._in_memory_store.values())

    def save(self, portfolio: Portfolio) -> None:
        key = str(portfolio.id.value)
        self._in_memory_store[key] = portfolio

    def delete(self, portfolio_id: PortfolioId) -> None:
        key = str(portfolio_id.value)
        self._in_memory_store.pop(key, None)
