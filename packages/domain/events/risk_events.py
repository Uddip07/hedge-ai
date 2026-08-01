"""
Risk & Margin Domain Events for the Indian AI Hedge Fund Platform.

Event definitions for risk limit breaches and broker account margin calls.
"""

import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.domain.enums.risk import RiskLevel
from packages.domain.events.base import DomainEvent
from packages.domain.utils.math import to_decimal
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.identifiers.uuid_wrappers import BrokerId, PortfolioId
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, kw_only=True)
class RiskLimitExceededEvent(DomainEvent):
    """
    Emitted when a portfolio risk threshold (VaR, Drawdown, Exposure) is exceeded.
    """

    portfolio_id: PortfolioId
    metric_name: str
    current_value: Decimal
    limit_threshold: Decimal
    severity: RiskLevel

    def __post_init__(self) -> None:
        DomainEvent.__post_init__(self)
        object.__setattr__(self, "current_value", to_decimal(self.current_value))
        object.__setattr__(self, "limit_threshold", to_decimal(self.limit_threshold))
        if not isinstance(self.severity, RiskLevel):
            object.__setattr__(self, "severity", RiskLevel(self.severity))

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "portfolio_id": self.portfolio_id.to_dict(),
                "metric_name": self.metric_name,
                "current_value": str(self.current_value),
                "limit_threshold": str(self.limit_threshold),
                "severity": self.severity.value,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RiskLimitExceededEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            portfolio_id=PortfolioId.from_dict(data["portfolio_id"]),
            metric_name=data["metric_name"],
            current_value=Decimal(str(data["current_value"])),
            limit_threshold=Decimal(str(data["limit_threshold"])),
            severity=RiskLevel(data["severity"]),
        )


@dataclass(frozen=True, kw_only=True)
class MarginCallEvent(DomainEvent):
    """
    Emitted when a broker account equity drops below maintenance margin requirement.
    """

    broker_account_id: BrokerId
    account_number: str
    available_equity: Money
    maintenance_margin: Money

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "broker_account_id": self.broker_account_id.to_dict(),
                "account_number": self.account_number,
                "available_equity": self.available_equity.to_dict(),
                "maintenance_margin": self.maintenance_margin.to_dict(),
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarginCallEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            broker_account_id=BrokerId.from_dict(data["broker_account_id"]),
            account_number=data["account_number"],
            available_equity=Money.from_dict(data["available_equity"]),
            maintenance_margin=Money.from_dict(data["maintenance_margin"]),
        )
