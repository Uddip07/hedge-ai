"""
Financial News & Sentiment Market Data Service.

Handles real-time news headlines, full articles, and market sentiment scores.
"""

from typing import cast

from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.infrastructure.market_data.models import NewsArticleModel
from packages.infrastructure.market_data.registries.quote_registry import (
    NewsProviderRegistry,
)
from packages.infrastructure.market_data.retry import RetryPolicy
from packages.infrastructure.market_data.telemetry import (
    MarketDataTelemetry,
    TelemetryTimer,
)


class NewsService:
    """Service wrapping news & sentiment operations."""

    def __init__(
        self,
        registry: NewsProviderRegistry,
        default_provider: str = "yahoo",
        retry_policy: RetryPolicy | None = None,
        telemetry: MarketDataTelemetry | None = None,
    ) -> None:
        self.registry = registry
        self.default_provider = default_provider
        self.retry_policy = retry_policy or RetryPolicy()
        self.telemetry = telemetry or MarketDataTelemetry()

    def get_news(self, ticker: Ticker, provider_name: str | None = None) -> list[NewsArticleModel]:
        prov_key = provider_name or self.default_provider
        provider = self.registry.lookup(prov_key)
        with TelemetryTimer() as timer:
            try:
                news = cast(
                    list[NewsArticleModel],
                    self.retry_policy.execute(lambda: provider.get_news(ticker)),
                )
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_news",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=True,
                )
                return news
            except Exception as err:
                self.telemetry.record_event(
                    provider=prov_key,
                    operation="get_news",
                    ticker=ticker.full_symbol,
                    latency_ms=timer.latency_ms,
                    cache_hit=False,
                    success=False,
                    failure_reason=str(err),
                )
                raise err
