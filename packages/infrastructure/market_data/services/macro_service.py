"""
Macroeconomic Indicator Market Data Service.

Handles central bank interest rates, inflation indicators, and economic data series.
"""

from typing import cast

from packages.infrastructure.market_data.models import MacroDataSeriesModel
from packages.infrastructure.market_data.registries.quote_registry import (
    MacroProviderRegistry,
)
from packages.infrastructure.market_data.retry import RetryPolicy
from packages.infrastructure.market_data.telemetry import (
    MarketDataTelemetry,
    TelemetryTimer,
)


class MacroService:
    """Service wrapping macroeconomic series queries."""

    def __init__(
        self,
        registry: MacroProviderRegistry,
        default_provider: str = "yahoo",
        retry_policy: RetryPolicy | None = None,
        telemetry: MarketDataTelemetry | None = None,
    ) -> None:
        self.registry = registry
        self.default_provider = default_provider
        self.retry_policy = retry_policy or RetryPolicy()
        self.telemetry = telemetry or MarketDataTelemetry()

    def get_macro_series(
        self, series_id: str, provider_name: str | None = None
    ) -> MacroDataSeriesModel:
        prov_key = provider_name or self.default_provider
        provider = self.registry.lookup(prov_key)
        with TelemetryTimer() as timer:
            try:
                series = cast(
                    MacroDataSeriesModel,
                    self.retry_policy.execute(lambda: provider.get_macro_series(series_id)),
                )
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_macro_series",
                    ticker=series_id,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=True,
                )
                return series
            except Exception as err:
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_macro_series",
                    ticker=series_id,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=False,
                    failure_reason=str(err),
                )
                raise err
