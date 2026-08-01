"""
SQL Portfolio Adapter — Production PortfolioPort Implementation.

Implements the application PortfolioPort by delegating to SQLPortfolioRepository
for persistent storage of Portfolio aggregates and valuation snapshots.
"""

from packages.application.ports.portfolio_port import PortfolioPort
from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.portfolio.snapshot import PortfolioSnapshot
from packages.domain.value_objects.identifiers.uuid_wrappers import PortfolioId
from packages.infrastructure.repositories.portfolio_repository import SQLPortfolioRepository


class SQLPortfolioAdapter(PortfolioPort):
    """
    Production Portfolio Port Adapter backed by SQLPortfolioRepository.

    This is the production implementation of PortfolioPort. It reads and writes
    Portfolio aggregates to the SQL store. Unlike MockPortfolioAdapter, portfolio
    data persists across application restarts and reflects the real portfolio state.
    """

    def __init__(self, repository: SQLPortfolioRepository | None = None) -> None:
        self._repo = repository or SQLPortfolioRepository()

    def get_portfolio_by_id(self, portfolio_id: PortfolioId) -> Portfolio | None:
        """Retrieve portfolio aggregate by ID from SQL store."""
        return self._repo.get_by_id(portfolio_id)

    def save_portfolio(self, portfolio: Portfolio) -> None:
        """Persist portfolio aggregate to SQL store."""
        self._repo.save(portfolio)

    def get_portfolio_snapshots(self, portfolio_id: PortfolioId) -> list[PortfolioSnapshot]:
        """
        Return historical portfolio snapshots.

        Currently returns an empty list — snapshot storage can be extended
        by adding a dedicated PortfolioSnapshotRepository.
        """
        return []
