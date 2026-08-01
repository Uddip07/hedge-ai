"""
Historical OHLCV Market Data Service.

Handles historical OHLCV bar feeds using registered Quote/Historical providers,
caching, retries, and telemetry.
"""

from typing import cast

from packages.domain.enums.market import Timeframe
from packages.domain.market.ohlcv import Candle
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp
from packages.infrastructure.market_data.cache import MarketDataCache
from packages.infrastructure.market_data.registries.quote_registry import (
    QuoteProviderRegistry,
)
from packages.infrastructure.market_data.retry import RetryPolicy
from packages.infrastructure.market_data.telemetry import (
    MarketDataTelemetry,
    TelemetryTimer,
)


class HistoricalService:
    """Service wrapping historical OHLCV candle bar operations."""

    def __init__(
        self,
        registry: QuoteProviderRegistry,
        default_provider: str = "yahoo",
        cache: MarketDataCache | None = None,
        retry_policy: RetryPolicy | None = None,
        telemetry: MarketDataTelemetry | None = None,
    ) -> None:
        self.registry = registry
        self.default_provider = default_provider
        self.cache = cache or MarketDataCache()
        self.retry_policy = retry_policy or RetryPolicy()
        self.telemetry = telemetry or MarketDataTelemetry()

    def get_historical_candles(
        self,
        ticker: Ticker,
        timeframe: Timeframe,
        start_time: Timestamp,
        end_time: Timestamp,
        provider_name: str | None = None,
    ) -> list[Candle]:
        prov_key = provider_name or self.default_provider
        cached = self.cache.get_candles(ticker, timeframe)
        if cached and isinstance(cached, list):
            self.telemetry.record_event(
                provider=prov_key,
                operation="get_historical_candles",
                ticker=ticker.full_symbol,
                latency_ms=0.1,
                cache_hit=True,
                success=True,
            )
            return cached

        provider = self.registry.lookup(prov_key)
        with TelemetryTimer() as timer:
            try:
                candles = cast(
                    list[Candle],
                    self.retry_policy.execute(
                        lambda: provider.get_historical_ohlcv(
                            ticker, timeframe, start_time, end_time
                        )
                    ),
                )
                self.cache.set_candles(ticker, timeframe, candles)
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_historical_candles",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=True,
                )
                return candles
            except Exception as err:
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_historical_candles",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=False,
                    failure_reason=str(err),
                )
                raise err
