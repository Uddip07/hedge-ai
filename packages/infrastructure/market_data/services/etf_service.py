"""
ETF Market Data Service.

Handles ETF NAV, AUM, category benchmarks, and constituent holdings.
"""

from typing import cast

from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.market_data.models import ETFInfoModel
from packages.infrastructure.market_data.registries.quote_registry import (
    ETFProviderRegistry,
)
from packages.infrastructure.market_data.retry import RetryPolicy
from packages.infrastructure.market_data.telemetry import (
    MarketDataTelemetry,
    TelemetryTimer,
)


class ETFService:
    """Service wrapping ETF information queries."""

    def __init__(
        self,
        registry: ETFProviderRegistry,
        default_provider: str = "yahoo",
        retry_policy: RetryPolicy | None = None,
        telemetry: MarketDataTelemetry | None = None,
    ) -> None:
        self.registry = registry
        self.default_provider = default_provider
        self.retry_policy = retry_policy or RetryPolicy()
        self.telemetry = telemetry or MarketDataTelemetry()

    def get_etf_info(self, ticker: Ticker, provider_name: str | None = None) -> ETFInfoModel:
        prov_key = provider_name or self.default_provider
        provider = self.registry.lookup(prov_key)
        with TelemetryTimer() as timer:
            try:
                etf_info = cast(
                    ETFInfoModel,
                    self.retry_policy.execute(lambda: provider.get_etf_info(ticker)),
                )
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_etf_info",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=True,
                )
                return etf_info
            except Exception as err:
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_etf_info",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=False,
                    failure_reason=str(err),
                )
                raise err
