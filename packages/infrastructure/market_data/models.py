"""
Market Data Models for Infrastructure Layer.

Defines data classes for MarketQuote, CorporateAction, MarketStatusInfo, NewsArticleModel,
FinancialStatementModel, MacroDataSeriesModel, and ETFInfoModel.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from packages.domain.enums.market import ExchangeType
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True)
class MarketQuote:
    """
    Market price quote snapshot model.
    """

    ticker: Ticker
    price: Price
    change_24h: Decimal = Decimal("0.00")
    volume_24h: Decimal = Decimal("0.00")
    timestamp: Timestamp = field(default_factory=Timestamp.now_utc)

    def to_dict(self) -> dict[str, Any]:
        """Serialize MarketQuote to dictionary."""
        return {
            "ticker": self.ticker.full_symbol,
            "price": str(self.price.amount),
            "currency": self.price.money.currency.code,
            "change_24h": str(self.change_24h),
            "volume_24h": str(self.volume_24h),
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True)
class CorporateAction:
    """
    Corporate action event model (Dividends, Splits, Bonus Shares, Rights Issue).
    """

    ticker: Ticker
    action_type: str
    record_date: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize CorporateAction to dictionary."""
        return {
            "ticker": self.ticker.full_symbol,
            "action_type": self.action_type,
            "record_date": self.record_date,
            "description": self.description,
        }


@dataclass(frozen=True)
class MarketStatusInfo:
    """
    Exchange session status information model.
    """

    exchange: ExchangeType
    is_open: bool
    session: str = "NORMAL"

    def to_dict(self) -> dict[str, Any]:
        """Serialize MarketStatusInfo to dictionary."""
        return {
            "exchange": self.exchange.value,
            "is_open": self.is_open,
            "session": self.session,
        }


@dataclass(frozen=True)
class NewsArticleModel:
    """
    News article model for market news and sentiment feeds.
    """

    ticker: Ticker
    title: str
    content: str
    source: str
    published_at: str
    url: str = ""
    sentiment_score: Decimal | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker.full_symbol,
            "title": self.title,
            "content": self.content,
            "source": self.source,
            "published_at": self.published_at,
            "url": self.url,
            "sentiment_score": (
                str(self.sentiment_score) if self.sentiment_score is not None else None
            ),
        }


@dataclass(frozen=True)
class FinancialStatementModel:
    """
    Financial statement model for Balance Sheet, Income Statement, Cash Flow, and Key Metrics.
    """

    ticker: Ticker
    statement_type: str
    period: str
    fiscal_year: int | None = None
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker.full_symbol,
            "statement_type": self.statement_type,
            "period": self.period,
            "fiscal_year": self.fiscal_year,
            "metrics": self.metrics,
        }


@dataclass(frozen=True)
class MacroDataSeriesModel:
    """
    Macroeconomic indicators & series model.
    """

    series_id: str
    name: str
    unit: str
    data_points: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "series_id": self.series_id,
            "name": self.name,
            "unit": self.unit,
            "data_points": self.data_points,
        }


@dataclass(frozen=True)
class ETFInfoModel:
    """
    ETF metadata and holdings model.
    """

    ticker: Ticker
    name: str
    category: str
    nav: Decimal = Decimal("0.00")
    aum: Decimal = Decimal("0.00")
    holdings: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker.full_symbol,
            "name": self.name,
            "category": self.category,
            "nav": str(self.nav),
            "aum": str(self.aum),
            "holdings": self.holdings,
        }
