"""
Market Data Cache Layer for Infrastructure.

Provides short-term TTL caching for market quotes, candles, and company profiles.
"""

from typing import Any

from packages.domain.enums.market import Timeframe
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.cache.base import BaseCache
from packages.infrastructure.cache.memory_cache import MemoryCacheAdapter


class MarketDataCache:
    """
    Cache wrapper for market data operations.
    """

    def __init__(
        self,
        cache_adapter: BaseCache | None = None,
        default_ttl_seconds: int = 60,
    ) -> None:
        self.cache = cache_adapter or MemoryCacheAdapter()
        self.default_ttl = default_ttl_seconds

    def _make_key(self, prefix: str, identifier: str) -> str:
        return f"market_data:{prefix}:{identifier}"

    def get_quote(self, ticker: Ticker) -> Any | None:
        """Retrieve cached quote payload."""
        key = self._make_key("quote", ticker.full_symbol)
        return self.cache.get(key)

    def set_quote(self, ticker: Ticker, quote_data: Any, ttl_seconds: int | None = None) -> None:
        """Store quote payload in cache."""
        key = self._make_key("quote", ticker.full_symbol)
        ttl = ttl_seconds or self.default_ttl
        self.cache.set(key, quote_data, ttl_seconds=ttl)

    def invalidate_quote(self, ticker: Ticker) -> None:
        """Invalidate cached quote for a ticker."""
        key = self._make_key("quote", ticker.full_symbol)
        self.cache.delete(key)

    def get_candles(self, ticker: Ticker, timeframe: Timeframe) -> Any | None:
        """Retrieve cached candle payload."""
        key = self._make_key("candles", f"{ticker.full_symbol}:{timeframe.value}")
        return self.cache.get(key)

    def set_candles(
        self,
        ticker: Ticker,
        timeframe: Timeframe,
        candles_data: Any,
        ttl_seconds: int | None = None,
    ) -> None:
        """Store candles payload in cache."""
        key = self._make_key("candles", f"{ticker.full_symbol}:{timeframe.value}")
        ttl = ttl_seconds or self.default_ttl
        self.cache.set(key, candles_data, ttl_seconds=ttl)

    def clear(self) -> None:
        """Clear all cached market data."""
        self.cache.clear()
