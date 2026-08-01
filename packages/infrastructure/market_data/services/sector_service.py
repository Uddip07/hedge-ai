"""
Sector Performance Market Data Service.

Handles sector performance metrics and industry classification statistics.
"""

from typing import Any, cast

from packages.infrastructure.market_data.registries.quote_registry import (
    FundamentalProviderRegistry,
)
from packages.infrastructure.market_data.retry import RetryPolicy
from packages.infrastructure.market_data.telemetry import (
    MarketDataTelemetry,
    TelemetryTimer,
)


class SectorService:
    """Service wrapping sector performance operations."""

    def __init__(
        self,
        registry: FundamentalProviderRegistry,
        default_provider: str = "yahoo",
        retry_policy: RetryPolicy | None = None,
        telemetry: MarketDataTelemetry | None = None,
    ) -> None:
        self.registry = registry
        self.default_provider = default_provider
        self.retry_policy = retry_policy or RetryPolicy()
        self.telemetry = telemetry or MarketDataTelemetry()

    def get_sector_performance(self, provider_name: str | None = None) -> dict[str, Any]:
        prov_key = provider_name or self.default_provider
        provider = self.registry.lookup(prov_key)
        with TelemetryTimer() as timer:
            try:
                sectors = cast(
                    dict[str, Any],
                    self.retry_policy.execute(lambda: provider.get_sector_performance()),
                )
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_sector_performance",
                    ticker="SECTORS",
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=True,
                )
                return sectors
            except Exception as err:
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_sector_performance",
                    ticker="SECTORS",
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=False,
                    failure_reason=str(err),
                )
                raise err
