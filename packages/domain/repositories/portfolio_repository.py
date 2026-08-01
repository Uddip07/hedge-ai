"""
Portfolio Repository Interface for the Indian AI Hedge Fund Platform.

Abstract repository specification for Portfolio Aggregate Root persistence.
Pure domain interface with zero infrastructure dependencies.
"""

from abc import ABC, abstractmethod

from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.value_objects.identifiers.uuid_wrappers import PortfolioId


class PortfolioRepository(ABC):
    """
    Abstract Repository Interface for Portfolio Aggregate Root persistence.
    """

    @abstractmethod
    def get_by_id(self, portfolio_id: PortfolioId) -> Portfolio | None:
        """Fetch Portfolio Aggregate Root by unique PortfolioId."""
        pass

    @abstractmethod
    def list_all(self) -> list[Portfolio]:
        """List all active portfolios."""
        pass

    @abstractmethod
    def save(self, portfolio: Portfolio) -> None:
        """Persist or update a Portfolio Aggregate Root."""
        pass

    @abstractmethod
    def delete(self, portfolio_id: PortfolioId) -> None:
        """Delete a Portfolio Aggregate Root by ID."""
        pass
