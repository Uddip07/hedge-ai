"""
MarketProvider Interface under packages/domain/market.

Defines domain-level abstract contract for real-time market quote retrieval,
historical candle feeds, company metadata, and market status checking.
"""

from abc import ABC, abstractmethod

from packages.domain.enums.market import ExchangeType, MarketStatus, Timeframe
from packages.domain.market.company import Company
from packages.domain.market.ohlcv import Candle
from packages.domain.market.quote import MarketQuote
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp


class MarketProvider(ABC):
    """
    Abstract Domain Market Provider Interface.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return unique provider identifier string (e.g. 'yahoo', 'nse')."""

    @abstractmethod
    def get_quote(self, ticker: Ticker) -> MarketQuote:
        """
        Fetch normalized real-time quote for a ticker.

        Args:
            ticker (Ticker): Asset ticker.

        Returns:
            MarketQuote: Normalized quote domain object.
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
        Fetch historical OHLCV candles.

        Args:
            ticker (Ticker): Asset ticker.
            timeframe (Timeframe): Bar aggregation window.
            start_time (Timestamp): Start time window.
            end_time (Timestamp): End time window.

        Returns:
            list[Candle]: Historical candle sequence.
        """

    @abstractmethod
    def get_company_profile(self, ticker: Ticker) -> Company | None:
        """
        Fetch company corporate profile.

        Args:
            ticker (Ticker): Asset ticker.

        Returns:
            Company | None: Company entity or None if unavailable.
        """

    @abstractmethod
    def get_market_status(self, exchange: ExchangeType) -> MarketStatus:
        """
        Detect real-time market status (PRE_OPEN, OPEN, CLOSED, POST_CLOSE).

        Args:
            exchange (ExchangeType): Exchange venue.

        Returns:
            MarketStatus: Current session state.
        """
