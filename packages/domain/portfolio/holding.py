"""
Holding Entity for the Indian AI Hedge Fund Domain.

Represents an asset holding inside a Portfolio aggregate with cost basis,
market evaluation, and unrealized PnL logic. Pure domain model.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.domain.exceptions import ValidationError
from packages.domain.utils.math import calculate_return
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.percentage import Percentage
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.core.quantity import Quantity
from packages.domain.value_objects.identifiers.ticker import Ticker


@dataclass
class Holding:
    """
    Holding Entity owned by Portfolio Aggregate Root.

    Attributes:
        ticker (Ticker): Ticker symbol value object.
        quantity (Quantity): Share quantity held.
        average_buy_price (Price): Weighted average cost basis price.
        current_price (Optional[Price]): Latest market evaluation price.
    """

    ticker: Ticker
    quantity: Quantity
    average_buy_price: Price
    current_price: Price | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.ticker, Ticker):
            object.__setattr__(self, "ticker", Ticker(self.ticker))
        if not isinstance(self.quantity, Quantity):
            object.__setattr__(self, "quantity", Quantity(self.quantity))
        if not isinstance(self.average_buy_price, Price):
            object.__setattr__(self, "average_buy_price", Price(self.average_buy_price))
        if self.current_price is not None and not isinstance(self.current_price, Price):
            object.__setattr__(self, "current_price", Price(self.current_price))

        if self.quantity.is_zero():
            raise ValidationError("Holding quantity cannot be zero.")

    @property
    def invested_value(self) -> Money:
        """Return total invested capital / cost basis (quantity * average_buy_price)."""
        return self.average_buy_price.money * self.quantity.value

    @property
    def current_value(self) -> Money:
        """Return current market evaluation value."""
        if self.current_price:
            return self.current_price.money * self.quantity.value
        return self.invested_value

    @property
    def unrealized_pnl(self) -> Money:
        """Return unrealized profit and loss (current_value - invested_value)."""
        return self.current_value - self.invested_value

    @property
    def unrealized_pnl_pct(self) -> Percentage:
        """Return unrealized PnL percentage return."""
        if self.invested_value.amount == Decimal("0"):
            return Percentage(Decimal("0.0"))
        ret = calculate_return(self.invested_value.amount, self.current_value.amount)
        return Percentage(ret)

    def update_price(self, new_price: Price) -> None:
        """Update market evaluation price."""
        object.__setattr__(self, "current_price", new_price)

    def add_shares(self, add_qty: Quantity, buy_price: Price) -> None:
        """
        Increase holding quantity and recalculate weighted average buy price.
        """
        new_total_qty = self.quantity + add_qty
        new_invested = self.invested_value + (buy_price.money * add_qty.value)
        new_avg_price = Price(money=new_invested / new_total_qty.value)

        object.__setattr__(self, "quantity", new_total_qty)
        object.__setattr__(self, "average_buy_price", new_avg_price)

    def add_quantity(self, add_qty: Quantity, buy_price: Price) -> "Holding":
        """Add quantity and return new updated Holding instance."""
        new_total_qty = self.quantity + add_qty
        new_invested = self.invested_value + (buy_price.money * add_qty.value)
        new_avg_price = Price(money=new_invested / new_total_qty.value)
        return Holding(
            ticker=self.ticker,
            quantity=new_total_qty,
            average_buy_price=new_avg_price,
            current_price=self.current_price,
        )

    def reduce_quantity(self, reduce_qty: Quantity) -> "Holding | None":
        """Reduce holding quantity and return updated Holding or None if empty."""
        if reduce_qty.value >= self.quantity.value:
            return None
        new_qty = self.quantity - reduce_qty
        return Holding(
            ticker=self.ticker,
            quantity=new_qty,
            average_buy_price=self.average_buy_price,
            current_price=self.current_price,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize Holding to dictionary."""
        return {
            "ticker": self.ticker.to_dict(),
            "quantity": self.quantity.to_dict(),
            "average_buy_price": self.average_buy_price.to_dict(),
            "current_price": self.current_price.to_dict() if self.current_price else None,
            "invested_value": self.invested_value.to_dict(),
            "current_value": self.current_value.to_dict(),
            "unrealized_pnl": self.unrealized_pnl.to_dict(),
            "unrealized_pnl_pct": self.unrealized_pnl_pct.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Holding":
        """Deserialize dictionary to Holding entity."""
        curr_p = Price.from_dict(data["current_price"]) if data.get("current_price") else None
        return cls(
            ticker=Ticker.from_dict(data["ticker"]),
            quantity=Quantity.from_dict(data["quantity"]),
            average_buy_price=Price.from_dict(data["average_buy_price"]),
            current_price=curr_p,
        )
