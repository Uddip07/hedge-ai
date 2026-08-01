"""
Company Profile Market Data Service.

Handles corporate company profile details and business overview resolution.
"""

from typing import cast

from packages.domain.market.company import Company
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.market_data.registries.quote_registry import (
    FundamentalProviderRegistry,
)
from packages.infrastructure.market_data.retry import RetryPolicy
from packages.infrastructure.market_data.telemetry import (
    MarketDataTelemetry,
    TelemetryTimer,
)


class CompanyProfileService:
    """Service wrapping company profile resolution."""

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

    def get_company_profile(self, ticker: Ticker, provider_name: str | None = None) -> Company:
        prov_key = provider_name or self.default_provider
        provider = self.registry.lookup(prov_key)
        with TelemetryTimer() as timer:
            try:
                company = cast(
                    Company,
                    self.retry_policy.execute(lambda: provider.get_company_profile(ticker)),
                )
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_company_profile",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=True,
                )
                return company
            except Exception as err:
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_company_profile",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=False,
                    failure_reason=str(err),
                )
                raise err
