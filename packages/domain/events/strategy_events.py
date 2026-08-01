"""
Strategy & Signal Domain Events for the Indian AI Hedge Fund Platform.

Event definitions for quantitative signal generation, strategy status changes, and optimization runs.
"""

import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.domain.enums.strategy import SignalType, StrategyStatus
from packages.domain.events.base import DomainEvent
from packages.domain.utils.math import to_decimal
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import StrategyId
from packages.domain.value_objects.metrics.scores import ConfidenceScore
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, kw_only=True)
class SignalGeneratedEvent(DomainEvent):
    """
    Emitted when a strategy generates a quantitative trading signal.
    """

    signal_id: uuid.UUID
    strategy_id: StrategyId
    ticker: Ticker
    signal_type: SignalType
    score: ConfidenceScore

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "signal_id": str(self.signal_id),
                "strategy_id": self.strategy_id.to_dict(),
                "ticker": self.ticker.to_dict(),
                "signal_type": self.signal_type.value,
                "score": self.score.to_dict(),
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SignalGeneratedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            signal_id=uuid.UUID(data["signal_id"]),
            strategy_id=StrategyId.from_dict(data["strategy_id"]),
            ticker=Ticker.from_dict(data["ticker"]),
            signal_type=SignalType(data["signal_type"]),
            score=ConfidenceScore.from_dict(data["score"]),
        )


@dataclass(frozen=True, kw_only=True)
class StrategyStatusChangedEvent(DomainEvent):
    """
    Emitted when a strategy operational status transitions (e.g., BACKTESTING to ACTIVE).
    """

    strategy_id: StrategyId
    previous_status: StrategyStatus
    new_status: StrategyStatus

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "strategy_id": self.strategy_id.to_dict(),
                "previous_status": self.previous_status.value,
                "new_status": self.new_status.value,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StrategyStatusChangedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            strategy_id=StrategyId.from_dict(data["strategy_id"]),
            previous_status=StrategyStatus(data["previous_status"]),
            new_status=StrategyStatus(data["new_status"]),
        )


@dataclass(frozen=True, kw_only=True)
class OptimizationCompletedEvent(DomainEvent):
    """
    Emitted when a parameter search optimization run completes.
    """

    optimization_id: uuid.UUID
    strategy_id: StrategyId
    best_score: Decimal

    def __post_init__(self) -> None:
        DomainEvent.__post_init__(self)
        object.__setattr__(self, "best_score", to_decimal(self.best_score))

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "optimization_id": str(self.optimization_id),
                "strategy_id": self.strategy_id.to_dict(),
                "best_score": str(self.best_score),
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OptimizationCompletedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            optimization_id=uuid.UUID(data["optimization_id"]),
            strategy_id=StrategyId.from_dict(data["strategy_id"]),
            best_score=Decimal(str(data["best_score"])),
        )
