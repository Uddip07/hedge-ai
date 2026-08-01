"""
Financial Fundamentals Market Data Service.

Handles annual and quarterly financial statements (Income Statements, Balance Sheets, Cash Flow Statements).
"""

from typing import cast

from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.market_data.models import FinancialStatementModel
from packages.infrastructure.market_data.registries.quote_registry import (
    FundamentalProviderRegistry,
)
from packages.infrastructure.market_data.retry import RetryPolicy
from packages.infrastructure.market_data.telemetry import (
    MarketDataTelemetry,
    TelemetryTimer,
)


class FundamentalService:
    """Service wrapping financial statement fundamental operations."""

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

    def get_income_statement(
        self, ticker: Ticker, provider_name: str | None = None
    ) -> FinancialStatementModel:
        prov_key = provider_name or self.default_provider
        provider = self.registry.lookup(prov_key)
        with TelemetryTimer() as timer:
            try:
                stmt = cast(
                    FinancialStatementModel,
                    self.retry_policy.execute(lambda: provider.get_income_statement(ticker)),
                )
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_income_statement",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=True,
                )
                return stmt
            except Exception as err:
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_income_statement",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=False,
                    failure_reason=str(err),
                )
                raise err

    def get_balance_sheet(
        self, ticker: Ticker, provider_name: str | None = None
    ) -> FinancialStatementModel:
        prov_key = provider_name or self.default_provider
        provider = self.registry.lookup(prov_key)
        with TelemetryTimer() as timer:
            try:
                stmt = cast(
                    FinancialStatementModel,
                    self.retry_policy.execute(lambda: provider.get_balance_sheet(ticker)),
                )
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_balance_sheet",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=True,
                )
                return stmt
            except Exception as err:
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_balance_sheet",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=False,
                    failure_reason=str(err),
                )
                raise err

    def get_cash_flow_statement(
        self, ticker: Ticker, provider_name: str | None = None
    ) -> FinancialStatementModel:
        prov_key = provider_name or self.default_provider
        provider = self.registry.lookup(prov_key)
        with TelemetryTimer() as timer:
            try:
                stmt = cast(
                    FinancialStatementModel,
                    self.retry_policy.execute(lambda: provider.get_cash_flow_statement(ticker)),
                )
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_cash_flow_statement",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=True,
                )
                return stmt
            except Exception as err:
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_cash_flow_statement",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=False,
                    failure_reason=str(err),
                )
                raise err
