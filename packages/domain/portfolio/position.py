"""
Position Entity for the Indian AI Hedge Fund Domain.

Represents an open or closed directional position (Long/Short) within a Portfolio aggregate.
Pure domain entity with zero infrastructure dependencies.
"""

import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from packages.domain.enums.trading import PositionType
from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.core.quantity import Quantity
from packages.domain.value_objects.identifiers import PortfolioId
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass
class Position:
    """
    Position Entity.

    Attributes:
        id (uuid.UUID): Unique position identifier.
        ticker (Ticker): Ticker symbol value object.
        position_type (PositionType): Direction (LONG / SHORT).
        quantity (Quantity): Position share quantity.
        entry_price (Price): Entry price.
        portfolio_id (PortfolioId | None): Optional parent portfolio identifier.
        current_price (Optional[Price]): Current market price.
        opened_at (Timestamp): Timestamp when opened.
        closed_at (Optional[Timestamp]): Timestamp when closed.
        realized_pnl_money (Optional[Money]): Realized PnL once closed.
    """

    ticker: Ticker
    position_type: PositionType
    quantity: Quantity
    entry_price: Price
    opened_at: Timestamp
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    portfolio_id: PortfolioId | None = None
    current_price: Price | None = None
    closed_at: Timestamp | None = None
    realized_pnl_money: Money | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.position_type, PositionType):
            object.__setattr__(self, "position_type", PositionType(self.position_type))
        if not isinstance(self.opened_at, Timestamp):
            object.__setattr__(self, "opened_at", Timestamp(self.opened_at))
        if self.portfolio_id is not None and not isinstance(self.portfolio_id, PortfolioId):
            object.__setattr__(self, "portfolio_id", PortfolioId(self.portfolio_id))

        if self.quantity.is_zero():
            raise ValidationError("Position quantity cannot be zero.")

    @property
    def is_open(self) -> bool:
        """Return True if position is currently open."""
        return self.closed_at is None

    @property
    def is_closed(self) -> bool:
        """Return True if position is closed."""
        return self.closed_at is not None

    @property
    def cost_basis(self) -> Money:
        """Return total position cost basis (quantity * entry_price)."""
        return self.entry_price.money * self.quantity.value

    @property
    def current_value(self) -> Money:
        """Return current position market value."""
        if self.current_price:
            return self.current_price.money * self.quantity.value
        return self.cost_basis

    @property
    def unrealized_pnl(self) -> Money:
        """Return unrealized profit and loss considering Long/Short direction."""
        if not self.is_open or not self.current_price:
            return Money(amount=Decimal("0"), currency=self.entry_price.money.currency)

        diff = self.current_price.money - self.entry_price.money
        mult = self.position_type.quantity_multiplier()
        return (diff * mult) * self.quantity.value

    def add_execution(self, add_qty: Quantity, add_price: Price) -> None:
        """Increase position quantity and recalculate entry price cost basis."""
        new_total_qty = self.quantity + add_qty
        new_invested = self.cost_basis + (add_price.money * add_qty.value)
        new_avg_price = Price(money=new_invested / new_total_qty.value)
        object.__setattr__(self, "quantity", new_total_qty)
        object.__setattr__(self, "entry_price", new_avg_price)

    def close_position(self, exit_price: Price, closed_at: Timestamp) -> Money:
        """
        Close position at exit_price and record realized PnL.

        Raises:
            ValidationError: If position is already closed.
        """
        if self.is_closed:
            raise ValidationError(f"Position '{self.id}' is already closed.")

        diff = exit_price.money - self.entry_price.money
        mult = self.position_type.quantity_multiplier()
        realized = (diff * mult) * self.quantity.value

        object.__setattr__(self, "closed_at", closed_at)
        object.__setattr__(self, "realized_pnl_money", realized)
        object.__setattr__(self, "current_price", exit_price)

        return realized

    def to_dict(self) -> dict[str, Any]:
        """Serialize Position to dictionary."""
        return {
            "id": str(self.id),
            "ticker": self.ticker.to_dict(),
            "position_type": self.position_type.value,
            "quantity": self.quantity.to_dict(),
            "entry_price": self.entry_price.to_dict(),
            "portfolio_id": self.portfolio_id.to_dict() if self.portfolio_id else None,
            "current_price": self.current_price.to_dict() if self.current_price else None,
            "opened_at": self.opened_at.to_dict(),
            "closed_at": self.closed_at.to_dict() if self.closed_at else None,
            "realized_pnl_money": (
                self.realized_pnl_money.to_dict() if self.realized_pnl_money else None
            ),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Position":
        """Deserialize dictionary to Position entity."""
        pid = PortfolioId.from_dict(data["portfolio_id"]) if data.get("portfolio_id") else None
        curr_p = Price.from_dict(data["current_price"]) if data.get("current_price") else None
        c_at = Timestamp.from_dict(data["closed_at"]) if data.get("closed_at") else None
        r_pnl = (
            Money.from_dict(data["realized_pnl_money"]) if data.get("realized_pnl_money") else None
        )

        return cls(
            id=uuid.UUID(data["id"]),
            ticker=Ticker.from_dict(data["ticker"]),
            position_type=PositionType(data["position_type"]),
            quantity=Quantity.from_dict(data["quantity"]),
            entry_price=Price.from_dict(data["entry_price"]),
            portfolio_id=pid,
            current_price=curr_p,
            opened_at=Timestamp.from_dict(data["opened_at"]),
            closed_at=c_at,
            realized_pnl_money=r_pnl,
        )
