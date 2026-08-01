"""
Price History Repository Interface for the Indian AI Hedge Fund Platform.

Pure domain interface for historical price queries.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class PriceHistoryRepository(ABC):
    """
    Abstract Repository Interface for Price History persistence and retrieval.
    """

    @abstractmethod
    def get_company_history(
        self, symbol: str, start_date: date | None = None, end_date: date | None = None
    ) -> list[dict[str, Any]]:
        """Load company historical daily prices."""
        pass

    @abstractmethod
    def get_rolling_window(
        self, symbol: str, end_date: date, window_days: int
    ) -> list[dict[str, Any]]:
        """Load trailing window of historical candles as of end_date."""
        pass

    @abstractmethod
    def get_previous_n_candles(self, symbol: str, end_date: date, n: int) -> list[dict[str, Any]]:
        """Load previous N candles strictly prior to or on end_date."""
        pass

    @abstractmethod
    def get_market_snapshot(self, as_of_date: date) -> list[dict[str, Any]]:
        """Load closing snapshot across all market companies as of date."""
        pass

    @abstractmethod
    def get_sector_history(
        self, sector: str, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        """Load price records for all companies belonging to a sector."""
        pass
