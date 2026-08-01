"""
Portfolio Port Interface for the Application Layer.

Defines outbound port contracts for portfolio aggregate querying, persistence,
and historical valuation snapshots.
"""

from abc import ABC, abstractmethod

from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.portfolio.snapshot import PortfolioSnapshot
from packages.domain.value_objects.identifiers.uuid_wrappers import PortfolioId


class PortfolioPort(ABC):
    """
    Abstract Outbound Port for Portfolio Data Management and Valuation Services.
    """

    @abstractmethod
    def get_portfolio_by_id(self, portfolio_id: PortfolioId) -> Portfolio | None:
        """
        Retrieve portfolio aggregate root by ID.

        Args:
            portfolio_id (PortfolioId): Unique portfolio identifier.

        Returns:
            Portfolio | None: Portfolio aggregate root or None if not found.
        """

    @abstractmethod
    def save_portfolio(self, portfolio: Portfolio) -> None:
        """
        Persist or update portfolio aggregate root.

        Args:
            portfolio (Portfolio): Portfolio aggregate root to store.
        """

    @abstractmethod
    def get_portfolio_snapshots(self, portfolio_id: PortfolioId) -> list[PortfolioSnapshot]:
        """
        Retrieve historical point-in-time equity snapshots for a portfolio.

        Args:
            portfolio_id (PortfolioId): Unique portfolio identifier.

        Returns:
            list[PortfolioSnapshot]: Chronologically ordered list of snapshots.
        """
