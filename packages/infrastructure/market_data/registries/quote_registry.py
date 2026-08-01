"""
Category-Specific Provider Registries.

Provides QuoteProviderRegistry, FundamentalProviderRegistry, NewsProviderRegistry,
MacroProviderRegistry, CorporateActionProviderRegistry, and ETFProviderRegistry.
"""

from typing import Any

from packages.infrastructure.market_data.registries.base_registry import BaseProviderRegistry


class QuoteProviderRegistry(BaseProviderRegistry[Any]):
    def __init__(self) -> None:
        super().__init__("Quotes & Historical OHLCV")


class FundamentalProviderRegistry(BaseProviderRegistry[Any]):
    def __init__(self) -> None:
        super().__init__("Financial Fundamentals & Statements")


class NewsProviderRegistry(BaseProviderRegistry[Any]):
    def __init__(self) -> None:
        super().__init__("Market News & Sentiment")


class MacroProviderRegistry(BaseProviderRegistry[Any]):
    def __init__(self) -> None:
        super().__init__("Macroeconomic Data & Calendar")


class CorporateActionProviderRegistry(BaseProviderRegistry[Any]):
    def __init__(self) -> None:
        super().__init__("Corporate Actions & Dividends")


class ETFProviderRegistry(BaseProviderRegistry[Any]):
    def __init__(self) -> None:
        super().__init__("ETF & Sector Information")
