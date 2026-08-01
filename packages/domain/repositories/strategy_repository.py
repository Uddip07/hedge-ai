"""
Strategy Repository Interface for the Indian AI Hedge Fund Platform.

Abstract repository specification for Strategy Aggregate Root persistence.
Pure domain interface with zero infrastructure dependencies.
"""

from abc import ABC, abstractmethod

from packages.domain.strategy.strategy import Strategy
from packages.domain.value_objects.identifiers.uuid_wrappers import StrategyId


class StrategyRepository(ABC):
    """
    Abstract Repository Interface for Strategy Aggregate Root persistence.
    """

    @abstractmethod
    def get_by_id(self, strategy_id: StrategyId) -> Strategy | None:
        """Fetch Strategy Aggregate Root by unique StrategyId."""
        pass

    @abstractmethod
    def list_active(self) -> list[Strategy]:
        """List all actively deployed quantitative strategies."""
        pass

    @abstractmethod
    def list_all(self) -> list[Strategy]:
        """List all strategies."""
        pass

    @abstractmethod
    def save(self, strategy: Strategy) -> None:
        """Persist or update a Strategy Aggregate Root."""
        pass

    @abstractmethod
    def delete(self, strategy_id: StrategyId) -> None:
        """Delete a Strategy Aggregate Root by ID."""
        pass
