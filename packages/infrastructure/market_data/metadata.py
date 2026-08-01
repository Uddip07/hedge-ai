"""
Provider Metadata for Market Data Infrastructure.

Defines structures for declaring, querying, and discovering provider capabilities across
categories (Quotes, History, Fundamentals, News, Macro, Corporate Actions, ETFs, Sectors).
"""

from dataclasses import dataclass, field
from typing import Any

from packages.domain.enums.market import ExchangeType


@dataclass(frozen=True, slots=True)
class ProviderMetadata:
    """
    Metadata and capability descriptor for a Market Intelligence Provider.
    """

    provider_name: str
    provider_version: str
    supported_markets: list[str] = field(default_factory=lambda: ["IN", "US", "UK"])
    supported_assets: list[str] = field(default_factory=lambda: ["EQUITY", "ETF", "INDEX"])
    supported_features: list[str] = field(
        default_factory=lambda: [
            "QUOTES",
            "HISTORY",
            "FUNDAMENTALS",
            "NEWS",
            "MACRO",
            "CORPORATE_ACTIONS",
            "ETF",
        ]
    )
    supported_exchanges: list[ExchangeType] = field(
        default_factory=lambda: [
            ExchangeType.NSE,
            ExchangeType.BSE,
            ExchangeType.NYSE,
            ExchangeType.NASDAQ,
        ]
    )

    supports_quotes: bool = True
    supports_history: bool = True
    supports_fundamentals: bool = True
    supports_news: bool = True
    supports_macro: bool = True
    supports_corporate_actions: bool = True
    supports_etf: bool = True
    supports_intraday: bool = True
    supports_streaming: bool = False
    supports_options: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serialize ProviderMetadata to dictionary."""
        return {
            "provider_name": self.provider_name,
            "provider_version": self.provider_version,
            "supported_markets": self.supported_markets,
            "supported_assets": self.supported_assets,
            "supported_features": self.supported_features,
            "supported_exchanges": [ex.value for ex in self.supported_exchanges],
            "capabilities": {
                "supports_quotes": self.supports_quotes,
                "supports_history": self.supports_history,
                "supports_fundamentals": self.supports_fundamentals,
                "supports_news": self.supports_news,
                "supports_macro": self.supports_macro,
                "supports_corporate_actions": self.supports_corporate_actions,
                "supports_etf": self.supports_etf,
                "supports_intraday": self.supports_intraday,
                "supports_streaming": self.supports_streaming,
                "supports_options": self.supports_options,
            },
        }
