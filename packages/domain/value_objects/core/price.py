"""
Price Value Object for the Indian AI Hedge Fund Domain.

Represents a non-negative asset market price wrapping Money. Immutable and self-validating.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.domain.exceptions import ValidationError
from packages.domain.utils.math import to_decimal
from packages.domain.value_objects.core.money import Money


@dataclass(frozen=True, slots=True)
class Price:
    """
    Immutable value object for asset unit prices.

    Attributes:
        money (Money): Price monetary amount.
    """

    money: Money

    def __post_init__(self) -> None:
        if not isinstance(self.money, Money):
            raise ValidationError("Price must wrap a valid Money instance.")
        if self.money.is_negative():
            raise ValidationError(
                f"Asset price cannot be negative. Got {self.money.amount}.",
                context={"amount": str(self.money.amount)},
            )

    @classmethod
    def from_amount(cls, amount: int | float | str | Decimal, currency: Any = "INR") -> "Price":
        """Factory method to construct Price directly from amount and currency."""
        return cls(money=Money(amount=to_decimal(amount), currency=currency))

    @property
    def amount(self) -> Decimal:
        """Return raw Decimal price amount."""
        return self.money.amount

    def __add__(self, other: "Price") -> "Price":
        return Price(money=self.money + other.money)

    def __sub__(self, other: "Price") -> "Price":
        res_money = self.money - other.money
        if res_money.is_negative():
            raise ValidationError("Price difference cannot result in a negative price.")
        return Price(money=res_money)

    def __mul__(self, scalar: int | float | Decimal) -> "Price":
        return Price(money=self.money * scalar)

    def __rmul__(self, scalar: int | float | Decimal) -> "Price":
        return self.__mul__(scalar)

    def __truediv__(self, scalar: int | float | Decimal) -> "Price":
        return Price(money=self.money / scalar)

    def __lt__(self, other: "Price") -> bool:
        return self.money < other.money

    def __le__(self, other: "Price") -> bool:
        return self.money <= other.money

    def __gt__(self, other: "Price") -> bool:
        return self.money > other.money

    def __ge__(self, other: "Price") -> bool:
        return self.money >= other.money

    def to_dict(self) -> dict[str, Any]:
        """Serialize Price to dictionary."""
        return {"money": self.money.to_dict()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Price":
        """Deserialize dictionary to Price value object."""
        return cls(money=Money.from_dict(data["money"]))

    def __str__(self) -> str:
        return str(self.money)
