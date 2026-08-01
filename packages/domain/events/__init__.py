"""
Domain Events Package for the Indian AI Hedge Fund Platform.

Consolidates immutable domain event classes across all bounded contexts:
Market, Trading, Portfolio, Strategy, Research, Risk, and AI Agents.
"""

from packages.domain.events.ai_events import AgentThoughtGeneratedEvent, ToolExecutedEvent
from packages.domain.events.base import DomainEvent
from packages.domain.events.market_events import (
    BarClosedEvent,
    MarketSessionChangedEvent,
    PriceUpdatedEvent,
)
from packages.domain.events.portfolio_events import (
    CashDepositedEvent,
    CashWithdrawnEvent,
    PortfolioCreatedEvent,
    PortfolioSnapshotCreatedEvent,
    PositionClosedEvent,
)
from packages.domain.events.research_events import (
    ConsensusReachedEvent,
    ResearchReportApprovedEvent,
    ResearchReportCreatedEvent,
)
from packages.domain.events.risk_events import MarginCallEvent, RiskLimitExceededEvent
from packages.domain.events.strategy_events import (
    OptimizationCompletedEvent,
    SignalGeneratedEvent,
    StrategyStatusChangedEvent,
)
from packages.domain.events.trading_events import (
    OrderCancelledEvent,
    OrderFilledEvent,
    OrderPlacedEvent,
    TradeExecutedEvent,
)

__all__ = [
    "DomainEvent",
    # Market Events
    "MarketSessionChangedEvent",
    "PriceUpdatedEvent",
    "BarClosedEvent",
    # Trading Events
    "OrderPlacedEvent",
    "OrderFilledEvent",
    "OrderCancelledEvent",
    "TradeExecutedEvent",
    # Portfolio Events
    "PortfolioCreatedEvent",
    "CashDepositedEvent",
    "CashWithdrawnEvent",
    "PositionClosedEvent",
    "PortfolioSnapshotCreatedEvent",
    # Strategy Events
    "SignalGeneratedEvent",
    "StrategyStatusChangedEvent",
    "OptimizationCompletedEvent",
    # Research Events
    "ResearchReportCreatedEvent",
    "ConsensusReachedEvent",
    "ResearchReportApprovedEvent",
    # Risk Events
    "RiskLimitExceededEvent",
    "MarginCallEvent",
    # AI Events
    "AgentThoughtGeneratedEvent",
    "ToolExecutedEvent",
]
