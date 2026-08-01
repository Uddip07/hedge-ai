"""
Portfolio Domain Events for the Indian AI Hedge Fund Platform.

Event definitions for portfolio creation, cash deposits/withdrawals, holdings updates,
position closures, rebalancing, and snapshots.
"""

import uuid
from dataclasses import dataclass
from typing import Any

from packages.domain.enums.portfolio import PortfolioType
from packages.domain.events.base import DomainEvent
from packages.domain.portfolio.snapshot import PortfolioSnapshot
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import PortfolioId
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, kw_only=True)
class PortfolioCreatedEvent(DomainEvent):
    """
    Emitted when a new portfolio aggregate root is initialized.
    """

    portfolio_id: PortfolioId
    name: str
    portfolio_type: PortfolioType

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "portfolio_id": self.portfolio_id.to_dict(),
                "name": self.name,
                "portfolio_type": self.portfolio_type.value,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PortfolioCreatedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            portfolio_id=PortfolioId.from_dict(data["portfolio_id"]),
            name=data["name"],
            portfolio_type=PortfolioType(data["portfolio_type"]),
        )


@dataclass(frozen=True, kw_only=True)
class CashDepositedEvent(DomainEvent):
    """
    Emitted when cash is deposited into portfolio balance.
    """

    portfolio_id: PortfolioId
    amount: Money
    new_balance: Money

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "portfolio_id": self.portfolio_id.to_dict(),
                "amount": self.amount.to_dict(),
                "new_balance": self.new_balance.to_dict(),
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CashDepositedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            portfolio_id=PortfolioId.from_dict(data["portfolio_id"]),
            amount=Money.from_dict(data["amount"]),
            new_balance=Money.from_dict(data["new_balance"]),
        )


@dataclass(frozen=True, kw_only=True)
class CashWithdrawnEvent(DomainEvent):
    """
    Emitted when cash is withdrawn from portfolio balance.
    """

    portfolio_id: PortfolioId
    amount: Money
    new_balance: Money

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "portfolio_id": self.portfolio_id.to_dict(),
                "amount": self.amount.to_dict(),
                "new_balance": self.new_balance.to_dict(),
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CashWithdrawnEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            portfolio_id=PortfolioId.from_dict(data["portfolio_id"]),
            amount=Money.from_dict(data["amount"]),
            new_balance=Money.from_dict(data["new_balance"]),
        )


@dataclass(frozen=True, kw_only=True)
class PositionClosedEvent(DomainEvent):
    """
    Emitted when an open portfolio position is closed.
    """

    portfolio_id: PortfolioId
    position_id: uuid.UUID
    ticker: Ticker
    realized_pnl: Money

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "portfolio_id": self.portfolio_id.to_dict(),
                "position_id": str(self.position_id),
                "ticker": self.ticker.to_dict(),
                "realized_pnl": self.realized_pnl.to_dict(),
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PositionClosedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            portfolio_id=PortfolioId.from_dict(data["portfolio_id"]),
            position_id=uuid.UUID(data["position_id"]),
            ticker=Ticker.from_dict(data["ticker"]),
            realized_pnl=Money.from_dict(data["realized_pnl"]),
        )


@dataclass(frozen=True, kw_only=True)
class PortfolioSnapshotCreatedEvent(DomainEvent):
    """
    Emitted when a portfolio point-in-time state snapshot is recorded.
    """

    portfolio_id: PortfolioId
    snapshot: PortfolioSnapshot

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "portfolio_id": self.portfolio_id.to_dict(),
                "snapshot": self.snapshot.to_dict(),
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PortfolioSnapshotCreatedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            portfolio_id=PortfolioId.from_dict(data["portfolio_id"]),
            snapshot=PortfolioSnapshot.from_dict(data["snapshot"]),
        )
