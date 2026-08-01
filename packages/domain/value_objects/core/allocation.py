"""
Allocation Value Object for the Indian AI Hedge Fund Domain.

Represents a portfolio position target allocation linking a Ticker to a Weight
and an optional Money target amount. Immutable and self-validating.
"""

from dataclasses import dataclass
from typing import Any

from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.weight import Weight
from packages.domain.value_objects.identifiers.ticker import Ticker


@dataclass(frozen=True, slots=True)
class Allocation:
    """
    Immutable value object for asset target allocation in rebalancing models.

    Attributes:
        ticker (Ticker): Ticker value object.
        weight (Weight): Target portfolio weight.
        target_money (Optional[Money]): Calculated monetary target value.
    """

    ticker: Ticker
    weight: Weight
    target_money: Money | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.ticker, Ticker):
            raise ValidationError("Allocation must bind a valid Ticker instance.")
        if not isinstance(self.weight, Weight):
            raise ValidationError("Allocation must bind a valid Weight instance.")
        if self.target_money is not None and not isinstance(self.target_money, Money):
            raise ValidationError("target_money must be a valid Money instance or None.")

    def with_target_money(self, money: Money) -> "Allocation":
        """Return a new Allocation with target_money set."""
        return Allocation(ticker=self.ticker, weight=self.weight, target_money=money)

    def to_dict(self) -> dict[str, Any]:
        """Serialize Allocation to dictionary."""
        return {
            "ticker": self.ticker.to_dict(),
            "weight": self.weight.to_dict(),
            "target_money": self.target_money.to_dict() if self.target_money else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Allocation":
        """Deserialize dictionary to Allocation value object."""
        ticker = Ticker.from_dict(data["ticker"])
        weight = Weight.from_dict(data["weight"])
        target_money = Money.from_dict(data["target_money"]) if data.get("target_money") else None
        return cls(ticker=ticker, weight=weight, target_money=target_money)

    def __str__(self) -> str:
        if self.target_money:
            return f"{self.ticker.full_symbol}: {self.weight} ({self.target_money})"
        return f"{self.ticker.full_symbol}: {self.weight}"
