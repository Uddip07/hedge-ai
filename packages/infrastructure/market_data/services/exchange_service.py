"""
Exchange Metadata & Session Status Service.

Handles exchange session status, trading hours, and venue metadata resolution.
"""

from typing import Any, cast

from packages.domain.enums.market import ExchangeType
from packages.infrastructure.market_data.models import MarketStatusInfo
from packages.infrastructure.market_data.registries.quote_registry import (
    QuoteProviderRegistry,
)
from packages.infrastructure.market_data.retry import RetryPolicy
from packages.infrastructure.market_data.telemetry import (
    MarketDataTelemetry,
    TelemetryTimer,
)


class ExchangeService:
    """Service wrapping exchange status and metadata operations."""

    def __init__(
        self,
        registry: QuoteProviderRegistry,
        default_provider: str = "yahoo",
        retry_policy: RetryPolicy | None = None,
        telemetry: MarketDataTelemetry | None = None,
    ) -> None:
        self.registry = registry
        self.default_provider = default_provider
        self.retry_policy = retry_policy or RetryPolicy()
        self.telemetry = telemetry or MarketDataTelemetry()

    def get_market_status(
        self, exchange: ExchangeType, provider_name: str | None = None
    ) -> MarketStatusInfo:
        prov_key = provider_name or self.default_provider
        provider = self.registry.lookup(prov_key)
        with TelemetryTimer() as timer:
            try:
                status_info = cast(
                    MarketStatusInfo,
                    self.retry_policy.execute(lambda: provider.get_market_status(exchange)),
                )
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_market_status",
                    ticker=exchange.value,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=True,
                )
                return status_info
            except Exception as err:
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_market_status",
                    ticker=exchange.value,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=False,
                    failure_reason=str(err),
                )
                raise err

    def get_exchange_metadata(
        self, exchange: ExchangeType, provider_name: str | None = None
    ) -> dict[str, Any]:
        prov_key = provider_name or self.default_provider
        provider = self.registry.lookup(prov_key)
        with TelemetryTimer() as timer:
            try:
                meta = cast(
                    dict[str, Any],
                    self.retry_policy.execute(lambda: provider.get_exchange_metadata(exchange)),
                )
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_exchange_metadata",
                    ticker=exchange.value,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=True,
                )
                return meta
            except Exception as err:
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_exchange_metadata",
                    ticker=exchange.value,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=False,
                    failure_reason=str(err),
                )
                raise err
