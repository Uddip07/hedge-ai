"""
Value Objects Package Root for the Indian AI Hedge Fund Domain.
"""

from packages.domain.value_objects.core import (
    Allocation,
    Money,
    Percentage,
    Price,
    Quantity,
    SectorWeight,
    Weight,
)
from packages.domain.value_objects.identifiers import (
    ISIN,
    BacktestId,
    BrokerId,
    Currency,
    DocumentId,
    EntityId,
    ExecutionId,
    OrderId,
    PortfolioId,
    PromptId,
    ResearchId,
    StrategyId,
    Ticker,
    TradeId,
    UserId,
)
from packages.domain.value_objects.metrics import (
    ATR,
    MACD,
    RSI,
    ConfidenceScore,
    Drawdown,
    RecommendationScore,
    RiskScore,
    SharpeRatio,
    SortinoRatio,
    Volatility,
)
from packages.domain.value_objects.temporal import (
    FiscalYear,
    MarketTimestamp,
    PriceRange,
    ReportingPeriod,
    Timestamp,
    TradingDate,
)

__all__ = [
    # Identifiers
    "Ticker",
    "ISIN",
    "Currency",
    "EntityId",
    "OrderId",
    "TradeId",
    "PortfolioId",
    "ResearchId",
    "StrategyId",
    "BacktestId",
    "BrokerId",
    "UserId",
    "PromptId",
    "DocumentId",
    "ExecutionId",
    # Core
    "Money",
    "Price",
    "Percentage",
    "Quantity",
    "Weight",
    "Allocation",
    "SectorWeight",
    # Metrics
    "RiskScore",
    "ConfidenceScore",
    "RecommendationScore",
    "SharpeRatio",
    "SortinoRatio",
    "Drawdown",
    "Volatility",
    "ATR",
    "RSI",
    "MACD",
    # Temporal
    "Timestamp",
    "MarketTimestamp",
    "TradingDate",
    "FiscalYear",
    "ReportingPeriod",
    "PriceRange",
]
