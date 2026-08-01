"""
Order Entity for the Indian AI Hedge Fund Domain.

Represents a trading order placed with a broker. Manages order lifecycle status,
fill accumulations, and execution event creation. Pure domain entity.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from packages.domain.brokerage.execution import Execution
from packages.domain.enums.trading import OrderStatus, OrderType, TradeType
from packages.domain.exceptions import OrderValidationError
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.core.quantity import Quantity
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import BrokerId, OrderId, PortfolioId
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass
class Order:
    """
    Order Entity owned by BrokerAccount Aggregate Root.

    Attributes:
        id (OrderId): Unique order identifier.
        portfolio_id (PortfolioId): Parent portfolio ID.
        broker_account_id (BrokerId): Parent broker account ID.
        ticker (Ticker): Target ticker symbol.
        order_type (OrderType): Order type instructions (LIMIT, MARKET, STOP_LOSS, etc.).
        trade_type (TradeType): Direction (BUY / SELL).
        quantity (Quantity): Target total share quantity.
        price (Optional[Price]): Limit price (required if order_type requires price).
        stop_price (Optional[Price]): Trigger price for stop orders.
        filled_quantity (Quantity): Accumulated filled quantity.
        status (OrderStatus): Order lifecycle status.
        created_at (Timestamp): Creation timestamp (UTC).
        updated_at (Timestamp): Last update timestamp (UTC).
    """

    portfolio_id: PortfolioId
    broker_account_id: BrokerId
    ticker: Ticker
    order_type: OrderType
    trade_type: TradeType
    quantity: Quantity
    id: OrderId = field(default_factory=OrderId.generate)
    price: Price | None = None
    stop_price: Price | None = None
    filled_quantity: Quantity = field(default_factory=lambda: Quantity(Decimal("0")))
    status: OrderStatus = OrderStatus.PENDING
    created_at: Timestamp = field(default_factory=Timestamp.now_utc)
    updated_at: Timestamp = field(default_factory=Timestamp.now_utc)

    def __post_init__(self) -> None:
        if not isinstance(self.id, OrderId):
            object.__setattr__(self, "id", OrderId(self.id))
        if not isinstance(self.portfolio_id, PortfolioId):
            object.__setattr__(self, "portfolio_id", PortfolioId(self.portfolio_id))
        if not isinstance(self.broker_account_id, BrokerId):
            object.__setattr__(self, "broker_account_id", BrokerId(self.broker_account_id))
        if not isinstance(self.order_type, OrderType):
            object.__setattr__(self, "order_type", OrderType(self.order_type))
        if not isinstance(self.trade_type, TradeType):
            object.__setattr__(self, "trade_type", TradeType(self.trade_type))
        if not isinstance(self.status, OrderStatus):
            object.__setattr__(self, "status", OrderStatus(self.status))
        if not isinstance(self.created_at, Timestamp):
            object.__setattr__(self, "created_at", Timestamp(self.created_at))

        if self.quantity.is_zero():
            raise OrderValidationError("Order quantity cannot be zero.")

        # Enforce order type requirements
        if self.order_type.requires_price() and self.price is None:
            raise OrderValidationError(
                f"Order type {self.order_type.value} requires a limit price.",
                context={"order_type": self.order_type.value},
            )

    @property
    def is_active(self) -> bool:
        """Return True if order is working and active."""
        return self.status.is_active()

    @property
    def is_terminal(self) -> bool:
        """Return True if order has reached a final state."""
        return self.status.is_terminal()

    @property
    def is_filled(self) -> bool:
        """Return True if order is completely filled."""
        return self.status.is_filled()

    @property
    def remaining_quantity(self) -> Quantity:
        """Return unfilled remaining share quantity."""
        return self.quantity - self.filled_quantity

    def fill(
        self,
        fill_quantity: Quantity,
        fill_price: Price,
        fee: Money | None = None,
        tax: Money | None = None,
        executed_at: Timestamp | None = None,
    ) -> Execution:
        """
        Apply a fill to the order, accumulating filled quantity and updating status.

        Returns:
            Execution: Emitted execution fill entity.
        """
        if not self.is_active:
            raise OrderValidationError(
                f"Cannot fill order '{self.id}' in terminal status {self.status.value}."
            )

        if fill_quantity > self.remaining_quantity:
            raise OrderValidationError(
                f"Fill quantity ({fill_quantity.value}) exceeds remaining order quantity ({self.remaining_quantity.value})."
            )

        new_filled = self.filled_quantity + fill_quantity
        object.__setattr__(self, "filled_quantity", new_filled)

        if new_filled == self.quantity:
            object.__setattr__(self, "status", OrderStatus.FILLED)
        else:
            object.__setattr__(self, "status", OrderStatus.PARTIALLY_FILLED)

        self._touch()

        fill_time = executed_at or Timestamp.now_utc()
        return Execution(
            order_id=self.id,
            ticker=self.ticker,
            trade_type=self.trade_type,
            quantity=fill_quantity,
            price=fill_price,
            fee=fee or Money(Decimal("0.00")),
            tax=tax or Money(Decimal("0.00")),
            executed_at=fill_time,
        )

    def cancel(self) -> None:
        """Cancel an active order."""
        if not self.is_active:
            raise OrderValidationError(
                f"Cannot cancel order '{self.id}' in status {self.status.value}."
            )
        object.__setattr__(self, "status", OrderStatus.CANCELLED)
        self._touch()

    def reject(self, reason: str = "") -> None:
        """Reject an order."""
        object.__setattr__(self, "status", OrderStatus.REJECTED)
        self._touch()

    def _touch(self) -> None:
        object.__setattr__(self, "updated_at", Timestamp.now_utc())

    def to_dict(self) -> dict[str, Any]:
        """Serialize Order entity to dictionary."""
        return {
            "id": self.id.to_dict(),
            "portfolio_id": self.portfolio_id.to_dict(),
            "broker_account_id": self.broker_account_id.to_dict(),
            "ticker": self.ticker.to_dict(),
            "order_type": self.order_type.value,
            "trade_type": self.trade_type.value,
            "quantity": self.quantity.to_dict(),
            "price": self.price.to_dict() if self.price else None,
            "stop_price": self.stop_price.to_dict() if self.stop_price else None,
            "filled_quantity": self.filled_quantity.to_dict(),
            "remaining_quantity": self.remaining_quantity.to_dict(),
            "status": self.status.value,
            "created_at": self.created_at.to_dict(),
            "updated_at": self.updated_at.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Order":
        """Deserialize dictionary to Order entity."""
        price_obj = Price.from_dict(data["price"]) if data.get("price") else None
        stop_p_obj = Price.from_dict(data["stop_price"]) if data.get("stop_price") else None

        return cls(
            id=OrderId.from_dict(data["id"]),
            portfolio_id=PortfolioId.from_dict(data["portfolio_id"]),
            broker_account_id=BrokerId.from_dict(data["broker_account_id"]),
            ticker=Ticker.from_dict(data["ticker"]),
            order_type=OrderType(data["order_type"]),
            trade_type=TradeType(data["trade_type"]),
            quantity=Quantity.from_dict(data["quantity"]),
            price=price_obj,
            stop_price=stop_p_obj,
            filled_quantity=Quantity.from_dict(data["filled_quantity"]),
            status=OrderStatus(data["status"]),
            created_at=Timestamp.from_dict(data["created_at"]),
            updated_at=Timestamp.from_dict(data["updated_at"]),
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Order):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)
