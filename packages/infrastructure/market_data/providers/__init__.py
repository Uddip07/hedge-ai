"""
Market Intelligence Providers Package.

Exports MarketDataProvider, DelegatingMarketDataProvider (formerly MockMarketDataProvider),
NSEMarketDataProvider, and YahooMarketDataProvider.
"""

from packages.infrastructure.market_data.providers.base import MarketDataProvider
from packages.infrastructure.market_data.providers.mock_provider import (
    DelegatingMarketDataProvider,
    MockMarketDataProvider,  # backward-compat alias
)
from packages.infrastructure.market_data.providers.nse_provider import (
    NSEMarketDataProvider,
)
from packages.infrastructure.market_data.providers.yahoo_provider import (
    YahooMarketDataProvider,
)

__all__ = [
    "DelegatingMarketDataProvider",
    "MarketDataProvider",
    "MockMarketDataProvider",
    "NSEMarketDataProvider",
    "YahooMarketDataProvider",
]
