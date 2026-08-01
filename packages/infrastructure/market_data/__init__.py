"""
Market Data Infrastructure Package.

Exports generic market data infrastructure components: normalizers, metadata descriptors,
category registries, response validators, retry policies, telemetry collectors, and infrastructure exceptions.
"""

from packages.infrastructure.market_data.configuration import MarketDataConfig
from packages.infrastructure.market_data.exceptions import (
    DataNotFoundError,
    FeatureNotSupportedError,
    MarketDataError,
    ProviderCapabilityError,
    ProviderConnectionError,
    ProviderTimeoutError,
    RateLimitError,
    ValidationMarketDataError,
)
from packages.infrastructure.market_data.health import MarketDataHealthCheck
from packages.infrastructure.market_data.metadata import ProviderMetadata
from packages.infrastructure.market_data.normalizers import (
    CurrencyNormalizer,
    ExchangeNormalizer,
    TickerNormalizer,
    TimeframeNormalizer,
)
from packages.infrastructure.market_data.registries import (
    BaseProviderRegistry,
    CorporateActionProviderRegistry,
    ETFProviderRegistry,
    FundamentalProviderRegistry,
    MacroProviderRegistry,
    NewsProviderRegistry,
    QuoteProviderRegistry,
)
from packages.infrastructure.market_data.retry import RetryPolicy
from packages.infrastructure.market_data.telemetry import (
    MarketDataTelemetry,
    TelemetryRecord,
    TelemetryTimer,
)
from packages.infrastructure.market_data.validators import (
    CorporateActionValidator,
    FundamentalValidator,
    MacroValidator,
    NewsValidator,
    QuoteValidator,
    ResponseValidator,
)

__all__ = [
    "MarketDataError",
    "FeatureNotSupportedError",
    "ProviderCapabilityError",
    "ProviderConnectionError",
    "ProviderTimeoutError",
    "DataNotFoundError",
    "ValidationMarketDataError",
    "RateLimitError",
    "MarketDataConfig",
    "ProviderMetadata",
    "TickerNormalizer",
    "CurrencyNormalizer",
    "ExchangeNormalizer",
    "TimeframeNormalizer",
    "BaseProviderRegistry",
    "QuoteProviderRegistry",
    "FundamentalProviderRegistry",
    "NewsProviderRegistry",
    "MacroProviderRegistry",
    "CorporateActionProviderRegistry",
    "ETFProviderRegistry",
    "ResponseValidator",
    "QuoteValidator",
    "FundamentalValidator",
    "NewsValidator",
    "MacroValidator",
    "CorporateActionValidator",
    "RetryPolicy",
    "MarketDataTelemetry",
    "TelemetryRecord",
    "TelemetryTimer",
    "MarketDataHealthCheck",
]
