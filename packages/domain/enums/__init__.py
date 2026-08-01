"""
Domain Enums Package for the Indian AI Hedge Fund Platform.

Consolidates all core system enums for market, trading, strategy, research, risk,
portfolio, AI, and system infrastructure domain models.
"""

from packages.domain.enums.ai import AgentType, ModelProvider
from packages.domain.enums.market import (
    ExchangeType,
    MarketSegment,
    MarketSession,
    MarketStatus,
    SettlementStatus,
    SettlementType,
    Timeframe,
)
from packages.domain.enums.portfolio import (
    AllocationMethod,
    CorporateActionType,
    PortfolioType,
    TaxType,
)
from packages.domain.enums.research import (
    DocumentType,
    RecommendationType,
    ResearchStatus,
)
from packages.domain.enums.risk import PerformanceMetric, RiskLevel, RiskMetric
from packages.domain.enums.strategy import (
    PaperTradeStatus,
    SignalStrength,
    SignalType,
    StrategyStatus,
    StrategyType,
)
from packages.domain.enums.system import BrokerType, CurrencyCode, NotificationPriority, UserRole
from packages.domain.enums.trading import (
    AssetType,
    ExecutionStatus,
    OrderStatus,
    OrderType,
    PositionType,
    ProductType,
    TradeType,
)

__all__ = [
    # Market Enums
    "ExchangeType",
    "MarketSegment",
    "MarketStatus",
    "SettlementType",
    "SettlementStatus",
    "MarketSession",
    "Timeframe",
    # Trading Enums
    "AssetType",
    "OrderType",
    "OrderStatus",
    "ProductType",
    "TradeType",
    "PositionType",
    "ExecutionStatus",
    # Strategy Enums
    "StrategyType",
    "StrategyStatus",
    "SignalType",
    "SignalStrength",
    "PaperTradeStatus",
    # Research Enums
    "ResearchStatus",
    "RecommendationType",
    "DocumentType",
    # Risk Enums
    "RiskLevel",
    "RiskMetric",
    "PerformanceMetric",
    # Portfolio Enums
    "PortfolioType",
    "AllocationMethod",
    "CorporateActionType",
    "TaxType",
    # AI Enums
    "ModelProvider",
    "AgentType",
    # System Enums
    "BrokerType",
    "NotificationPriority",
    "CurrencyCode",
    "UserRole",
]
