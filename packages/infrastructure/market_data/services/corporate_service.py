"""
Corporate Actions Market Data Service.

Handles dividend payouts, stock splits, bonus issues, and rights issues.
"""

from typing import cast

from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.market_data.models import CorporateAction
from packages.infrastructure.market_data.registries.quote_registry import (
    CorporateActionProviderRegistry,
)
from packages.infrastructure.market_data.retry import RetryPolicy
from packages.infrastructure.market_data.telemetry import (
    MarketDataTelemetry,
    TelemetryTimer,
)


class CorporateActionService:
    """Service wrapping corporate action operations."""

    def __init__(
        self,
        registry: CorporateActionProviderRegistry,
        default_provider: str = "yahoo",
        retry_policy: RetryPolicy | None = None,
        telemetry: MarketDataTelemetry | None = None,
    ) -> None:
        self.registry = registry
        self.default_provider = default_provider
        self.retry_policy = retry_policy or RetryPolicy()
        self.telemetry = telemetry or MarketDataTelemetry()

    def get_corporate_actions(
        self, ticker: Ticker, provider_name: str | None = None
    ) -> list[CorporateAction]:
        prov_key = provider_name or self.default_provider
        provider = self.registry.lookup(prov_key)
        with TelemetryTimer() as timer:
            try:
                actions = cast(
                    list[CorporateAction],
                    self.retry_policy.execute(lambda: provider.get_corporate_actions(ticker)),
                )
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_corporate_actions",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=True,
                )
                return actions
            except Exception as err:
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_corporate_actions",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=False,
                    failure_reason=str(err),
                )
                raise err
