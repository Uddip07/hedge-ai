"""
Economic Calendar Market Data Service.

Handles upcoming macroeconomic event calendars and central bank announcements.
"""

from typing import Any, cast

from packages.infrastructure.market_data.registries.quote_registry import (
    MacroProviderRegistry,
)
from packages.infrastructure.market_data.retry import RetryPolicy
from packages.infrastructure.market_data.telemetry import (
    MarketDataTelemetry,
    TelemetryTimer,
)


class EconomicCalendarService:
    """Service wrapping economic calendar queries."""

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

    def get_economic_calendar(
        self, country: str = "IN", provider_name: str | None = None
    ) -> list[dict[str, Any]]:
        prov_key = provider_name or self.default_provider
        provider = self.registry.lookup(prov_key)
        with TelemetryTimer() as timer:
            try:
                calendar = cast(
                    list[dict[str, Any]],
                    self.retry_policy.execute(lambda: provider.get_economic_calendar(country)),
                )
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_economic_calendar",
                    ticker=country,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=True,
                )
                return calendar
            except Exception as err:
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_economic_calendar",
                    ticker=country,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=False,
                    failure_reason=str(err),
                )
                raise err
