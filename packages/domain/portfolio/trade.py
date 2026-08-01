"""
Trade Entity for the Indian AI Hedge Fund Platform.

Represents an executed trade transaction within a Portfolio aggregate, capturing gross amount,
brokerage fees, and Indian transaction taxes (STT, GST, Stamp Duty). Pure domain entity.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from packages.domain.enums.trading import TradeType
from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.core.quantity import Quantity
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import (
    OrderId,
    PortfolioId,
    TradeId,
)
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass
class Trade:
    """
    Trade Entity.

    Attributes:
        id (TradeId): Unique trade identifier.
        portfolio_id (PortfolioId): Parent portfolio ID.
        order_id (OrderId): Originating order ID.
        ticker (Ticker): Executed ticker symbol.
        trade_type (TradeType): Execution direction (BUY / SELL).
        quantity (Quantity): Executed share quantity.
        price (Price): Execution unit price.
        fee (Money): Brokerage commission fee.
        tax (Money): Transaction taxes (STT, GST, Stamp Duty).
        executed_at (Timestamp): Execution timestamp (UTC).
    """

    portfolio_id: PortfolioId
    order_id: OrderId
    ticker: Ticker
    trade_type: TradeType
    quantity: Quantity
    price: Price
    executed_at: Timestamp
    id: TradeId = field(default_factory=TradeId.generate)
    fee: Money = field(default_factory=lambda: Money(Decimal("0.00")))
    tax: Money = field(default_factory=lambda: Money(Decimal("0.00")))

    def __post_init__(self) -> None:
        if not isinstance(self.id, TradeId):
            object.__setattr__(self, "id", TradeId(self.id))
        if not isinstance(self.portfolio_id, PortfolioId):
            object.__setattr__(self, "portfolio_id", PortfolioId(self.portfolio_id))
        if not isinstance(self.order_id, OrderId):
            object.__setattr__(self, "order_id", OrderId(self.order_id))
        if not isinstance(self.trade_type, TradeType):
            object.__setattr__(self, "trade_type", TradeType(self.trade_type))
        if not isinstance(self.executed_at, Timestamp):
            object.__setattr__(self, "executed_at", Timestamp(self.executed_at))

        if self.quantity.is_zero():
            raise ValidationError("Trade quantity cannot be zero.")

    @property
    def fees(self) -> Money:
        """Alias for fee to support alternative plural naming conventions."""
        return self.fee

    @property
    def is_closing_trade(self) -> bool:
        """Return True if this trade is a SELL transaction closing a position."""
        return self.trade_type == TradeType.SELL

    @property
    def gross_amount(self) -> Money:
        """Return gross trade transaction value (quantity * price)."""
        return self.price.money * self.quantity.value

    @property
    def total_frictions(self) -> Money:
        """Return combined fees and taxes."""
        return self.fee + self.tax

    @property
    def net_amount(self) -> Money:
        """
        Return net cash flow impact:
        - For BUY: gross + fee + tax (total cash debit)
        - For SELL: gross - fee - tax (total cash credit)
        """
        if self.trade_type.is_buy():
            return self.gross_amount + self.total_frictions
        return self.gross_amount - self.total_frictions

    def to_dict(self) -> dict[str, Any]:
        """Serialize Trade entity to dictionary."""
        return {
            "id": self.id.to_dict(),
            "portfolio_id": self.portfolio_id.to_dict(),
            "order_id": self.order_id.to_dict(),
            "ticker": self.ticker.to_dict(),
            "trade_type": self.trade_type.value,
            "quantity": self.quantity.to_dict(),
            "price": self.price.to_dict(),
            "fee": self.fee.to_dict(),
            "tax": self.tax.to_dict(),
            "gross_amount": self.gross_amount.to_dict(),
            "net_amount": self.net_amount.to_dict(),
            "executed_at": self.executed_at.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Trade":
        """Deserialize dictionary to Trade entity."""
        return cls(
            id=TradeId.from_dict(data["id"]),
            portfolio_id=PortfolioId.from_dict(data["portfolio_id"]),
            order_id=OrderId.from_dict(data["order_id"]),
            ticker=Ticker.from_dict(data["ticker"]),
            trade_type=TradeType(data["trade_type"]),
            quantity=Quantity.from_dict(data["quantity"]),
            price=Price.from_dict(data["price"]),
            fee=Money.from_dict(data["fee"]) if data.get("fee") else Money(Decimal("0.00")),
            tax=Money.from_dict(data["tax"]) if data.get("tax") else Money(Decimal("0.00")),
            executed_at=Timestamp.from_dict(data["executed_at"]),
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Trade):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)
