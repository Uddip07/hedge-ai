"""
Category Registries Package.

Exports category-specific provider registries: QuoteProviderRegistry, FundamentalProviderRegistry,
NewsProviderRegistry, MacroProviderRegistry, CorporateActionProviderRegistry, ETFProviderRegistry.
"""

from packages.infrastructure.market_data.registries.base_registry import BaseProviderRegistry
from packages.infrastructure.market_data.registries.quote_registry import (
    CorporateActionProviderRegistry,
    ETFProviderRegistry,
    FundamentalProviderRegistry,
    MacroProviderRegistry,
    NewsProviderRegistry,
    QuoteProviderRegistry,
)

__all__ = [
    "BaseProviderRegistry",
    "QuoteProviderRegistry",
    "FundamentalProviderRegistry",
    "NewsProviderRegistry",
    "MacroProviderRegistry",
    "CorporateActionProviderRegistry",
    "ETFProviderRegistry",
]
