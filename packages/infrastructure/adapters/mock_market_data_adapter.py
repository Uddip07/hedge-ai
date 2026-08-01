"""
Yahoo Market Data Adapter (Production) for Infrastructure Layer.

Implements MarketDataPort by wrapping Yahoo Finance via ProviderManager production pipeline.
Zero mock dependencies — all data is sourced live from Yahoo Finance (primary)
and NSE (fallback).
"""

from typing import Any

from packages.application.ports.market_data_port import MarketDataPort
from packages.domain.enums.market import ExchangeType, MarketStatus, Timeframe
from packages.domain.market.company import Company
from packages.domain.market.ohlcv import Candle
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp
from packages.infrastructure.market_data.cache import MarketDataCache
from packages.infrastructure.market_data.provider_manager import ProviderManager


class YahooMarketDataAdapter(MarketDataPort):
    """
    Production-grade Yahoo Finance Market Data Adapter implementing MarketDataPort.

    Delegates all provider operations to ProviderManager which chains:
      Primary: YahooMarketDataProvider (yfinance)
      Fallback: NSEMarketDataProvider

    This class is NOT a mock. It is the production market data entry point
    for the application layer.
    """

    def __init__(
        self,
        provider: Any = None,
        cache: MarketDataCache | None = None,
    ) -> None:
        self.cache = cache or MarketDataCache()
        self.manager = ProviderManager(
            primary_provider=provider,
            cache=self.cache,
        )
        self.provider = provider or self.manager.primary

    def get_latest_price(self, ticker: Ticker) -> Price:
        quote = self.manager.get_quote(ticker)
        return quote.price

    def get_historical_candles(
        self,
        ticker: Ticker,
        timeframe: Timeframe,
        start_time: Timestamp,
        end_time: Timestamp,
    ) -> list[Candle]:
        return self.manager.get_historical_candles(ticker, timeframe, start_time, end_time)

    def get_company_profile(self, ticker: Ticker) -> Company | None:
        return self.manager.get_company_profile(ticker)

    def is_market_open(self, exchange: ExchangeType) -> bool:
        """Return True if the market is in an active trading state."""
        status = self.manager.get_market_status(exchange)
        return status in (MarketStatus.OPEN, MarketStatus.PRE_OPEN)


# Backward-compatibility alias — prefer YahooMarketDataAdapter in new code.
MockMarketDataAdapter = YahooMarketDataAdapter
