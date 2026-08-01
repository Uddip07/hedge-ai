"""
Backtest Repository Interface for the Indian AI Hedge Fund Platform.

Abstract repository specification for Backtest Aggregate Root persistence.
Pure domain interface with zero infrastructure dependencies.
"""

from abc import ABC, abstractmethod

from packages.domain.backtesting.backtest import Backtest
from packages.domain.value_objects.identifiers.uuid_wrappers import BacktestId, StrategyId


class BacktestRepository(ABC):
    """
    Abstract Repository Interface for Backtest Aggregate Root persistence.
    """

    @abstractmethod
    def get_by_id(self, backtest_id: BacktestId) -> Backtest | None:
        """Fetch Backtest Aggregate Root by unique BacktestId."""
        pass

    @abstractmethod
    def list_by_strategy(self, strategy_id: StrategyId) -> list[Backtest]:
        """List all historical backtest runs associated with a StrategyId."""
        pass

    @abstractmethod
    def list_all(self) -> list[Backtest]:
        """List all backtest configurations."""
        pass

    @abstractmethod
    def save(self, backtest: Backtest) -> None:
        """Persist or update a Backtest Aggregate Root."""
        pass

    @abstractmethod
    def delete(self, backtest_id: BacktestId) -> None:
        """Delete a Backtest Aggregate Root by ID."""
        pass
