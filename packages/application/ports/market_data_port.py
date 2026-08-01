"""
Market Data Port Interface for the Application Layer.

Defines outbound port contracts for retrieving market prices, historical OHLCV candles,
exchange session states, and corporate metadata.
"""

from abc import ABC, abstractmethod

from packages.domain.enums.market import ExchangeType, Timeframe
from packages.domain.market.company import Company
from packages.domain.market.ohlcv import Candle
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp


class MarketDataPort(ABC):
    """
    Abstract Outbound Port for Market Data Provider integrations.
    """

    @abstractmethod
    def get_latest_price(self, ticker: Ticker) -> Price:
        """
        Fetch current market price for a given ticker.

        Args:
            ticker (Ticker): Target asset ticker identifier.

        Returns:
            Price: Latest market price object.
        """

    @abstractmethod
    def get_historical_candles(
        self,
        ticker: Ticker,
        timeframe: Timeframe,
        start_time: Timestamp,
        end_time: Timestamp,
    ) -> list[Candle]:
        """
        Retrieve historical OHLCV candles for a date range and timeframe.

        Args:
            ticker (Ticker): Target asset ticker identifier.
            timeframe (Timeframe): Bar aggregation period.
            start_time (Timestamp): Start time window (UTC).
            end_time (Timestamp): End time window (UTC).

        Returns:
            list[Candle]: Chronologically ordered list of OHLCV candles.
        """

    @abstractmethod
    def get_company_profile(self, ticker: Ticker) -> Company | None:
        """
        Retrieve company corporate profile for a given ticker.

        Args:
            ticker (Ticker): Target asset ticker identifier.

        Returns:
            Company | None: Company entity or None if not found.
        """

    @abstractmethod
    def is_market_open(self, exchange: ExchangeType) -> bool:
        """
        Check if the specified exchange venue is currently in open trading session.

        Args:
            exchange (ExchangeType): Target exchange venue.

        Returns:
            bool: True if market is currently open for trading.
        """
