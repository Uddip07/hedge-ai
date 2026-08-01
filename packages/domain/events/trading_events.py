"""
Trading Domain Events for the Indian AI Hedge Fund Platform.

Event definitions for order lifecycle (placed, filled, cancelled, rejected) and trade executions.
"""

import uuid
from dataclasses import dataclass
from typing import Any

from packages.domain.enums.trading import OrderType, TradeType
from packages.domain.events.base import DomainEvent
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.core.quantity import Quantity
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import (
    ExecutionId,
    OrderId,
    PortfolioId,
    TradeId,
)
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, kw_only=True)
class OrderPlacedEvent(DomainEvent):
    """
    Emitted when a new trading order is placed.
    """

    order_id: OrderId
    portfolio_id: PortfolioId
    ticker: Ticker
    order_type: OrderType
    trade_type: TradeType
    quantity: Quantity
    price: Price | None = None

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "order_id": self.order_id.to_dict(),
                "portfolio_id": self.portfolio_id.to_dict(),
                "ticker": self.ticker.to_dict(),
                "order_type": self.order_type.value,
                "trade_type": self.trade_type.value,
                "quantity": self.quantity.to_dict(),
                "price": self.price.to_dict() if self.price else None,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrderPlacedEvent":
        price_obj = Price.from_dict(data["price"]) if data.get("price") else None
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            order_id=OrderId.from_dict(data["order_id"]),
            portfolio_id=PortfolioId.from_dict(data["portfolio_id"]),
            ticker=Ticker.from_dict(data["ticker"]),
            order_type=OrderType(data["order_type"]),
            trade_type=TradeType(data["trade_type"]),
            quantity=Quantity.from_dict(data["quantity"]),
            price=price_obj,
        )


@dataclass(frozen=True, kw_only=True)
class OrderFilledEvent(DomainEvent):
    """
    Emitted when an order fill execution occurs.
    """

    order_id: OrderId
    execution_id: ExecutionId
    filled_quantity: Quantity
    fill_price: Price
    fee: Money
    tax: Money

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "order_id": self.order_id.to_dict(),
                "execution_id": self.execution_id.to_dict(),
                "filled_quantity": self.filled_quantity.to_dict(),
                "fill_price": self.fill_price.to_dict(),
                "fee": self.fee.to_dict(),
                "tax": self.tax.to_dict(),
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrderFilledEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            order_id=OrderId.from_dict(data["order_id"]),
            execution_id=ExecutionId.from_dict(data["execution_id"]),
            filled_quantity=Quantity.from_dict(data["filled_quantity"]),
            fill_price=Price.from_dict(data["fill_price"]),
            fee=Money.from_dict(data["fee"]),
            tax=Money.from_dict(data["tax"]),
        )


@dataclass(frozen=True, kw_only=True)
class OrderCancelledEvent(DomainEvent):
    """
    Emitted when an active order is cancelled.
    """

    order_id: OrderId
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "order_id": self.order_id.to_dict(),
                "reason": self.reason,
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrderCancelledEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            order_id=OrderId.from_dict(data["order_id"]),
            reason=data.get("reason", ""),
        )


@dataclass(frozen=True, kw_only=True)
class TradeExecutedEvent(DomainEvent):
    """
    Emitted when a trade transaction is logged to portfolio.
    """

    trade_id: TradeId
    portfolio_id: PortfolioId
    ticker: Ticker
    trade_type: TradeType
    quantity: Quantity
    price: Price
    net_amount: Money

    def to_dict(self) -> dict[str, Any]:
        d = DomainEvent.to_dict(self)
        d.update(
            {
                "trade_id": self.trade_id.to_dict(),
                "portfolio_id": self.portfolio_id.to_dict(),
                "ticker": self.ticker.to_dict(),
                "trade_type": self.trade_type.value,
                "quantity": self.quantity.to_dict(),
                "price": self.price.to_dict(),
                "net_amount": self.net_amount.to_dict(),
            }
        )
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TradeExecutedEvent":
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
            trade_id=TradeId.from_dict(data["trade_id"]),
            portfolio_id=PortfolioId.from_dict(data["portfolio_id"]),
            ticker=Ticker.from_dict(data["ticker"]),
            trade_type=TradeType(data["trade_type"]),
            quantity=Quantity.from_dict(data["quantity"]),
            price=Price.from_dict(data["price"]),
            net_amount=Money.from_dict(data["net_amount"]),
        )
