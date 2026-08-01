"""
Money Value Object for the Indian AI Hedge Fund Domain.

Represents a monetary value with currency binding. Uses pure Decimal arithmetic to prevent
IEEE-754 floating point artifacts. Immutable and self-validating.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.domain.enums.system import CurrencyCode
from packages.domain.exceptions import ValidationError
from packages.domain.utils.math import round_currency, to_decimal
from packages.domain.value_objects.identifiers.currency import Currency


@dataclass(frozen=True, slots=True)
class Money:
    """
    Immutable value object for monetary amounts.

    Attributes:
        amount (Decimal): Monetary value.
        currency (Currency): Currency value object (defaults to INR).
    """

    amount: Decimal
    currency: Currency = Currency(CurrencyCode.INR)

    def __post_init__(self) -> None:
        dec_amount = to_decimal(self.amount)
        object.__setattr__(self, "amount", dec_amount)
        if not isinstance(self.currency, Currency):
            object.__setattr__(self, "currency", Currency(self.currency))

    def rounded(self, decimals: int = 2) -> "Money":
        """Return a new Money instance rounded to specified currency decimals."""
        return Money(amount=round_currency(self.amount, decimals=decimals), currency=self.currency)

    def is_zero(self) -> bool:
        """Return True if amount is zero."""
        return self.amount == Decimal("0")

    def is_positive(self) -> bool:
        """Return True if amount > 0."""
        return self.amount > Decimal("0")

    def is_negative(self) -> bool:
        """Return True if amount < 0."""
        return self.amount < Decimal("0")

    def _check_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValidationError(
                f"Currency mismatch: cannot operate on {self.currency} and {other.currency}.",
                context={"curr_1": str(self.currency), "curr_2": str(other.currency)},
            )

    def __add__(self, other: "Money") -> "Money":
        self._check_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._check_currency(other)
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def __mul__(self, scalar: int | float | Decimal) -> "Money":
        dec_scalar = to_decimal(scalar)
        return Money(amount=self.amount * dec_scalar, currency=self.currency)

    def __rmul__(self, scalar: int | float | Decimal) -> "Money":
        return self.__mul__(scalar)

    def __truediv__(self, scalar: int | float | Decimal) -> "Money":
        dec_scalar = to_decimal(scalar)
        if dec_scalar == Decimal("0"):
            raise ValidationError("Cannot divide Money by zero.")
        return Money(amount=self.amount / dec_scalar, currency=self.currency)

    def __neg__(self) -> "Money":
        return Money(amount=-self.amount, currency=self.currency)

    def __abs__(self) -> "Money":
        return Money(amount=abs(self.amount), currency=self.currency)

    def __lt__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self.amount >= other.amount

    def allocate(self, ratios: list[int | float | Decimal]) -> list["Money"]:
        """
        Allocate monetary amount across ratios without losing fractional paisa/cents due to rounding.
        """
        if not ratios:
            raise ValidationError("Allocation ratios list cannot be empty.")

        dec_ratios = [to_decimal(r) for r in ratios]
        total_ratio = sum(dec_ratios)
        if total_ratio <= Decimal("0"):
            raise ValidationError("Sum of allocation ratios must be greater than zero.")

        # Allocate proportional rounded amounts
        remainder = self.amount
        results: list[Money] = []
        for r in dec_ratios:
            share = (self.amount * r) / total_ratio
            rounded_share = round_currency(share)
            results.append(Money(amount=rounded_share, currency=self.currency))
            remainder -= rounded_share

        # Distribute remainder paisa/cents one unit at a time to maintain total
        if remainder != Decimal("0"):
            unit = Decimal("0.01") if remainder > Decimal("0") else Decimal("-0.01")
            steps = int(abs(remainder) / Decimal("0.01"))
            for i in range(steps):
                idx = i % len(results)
                results[idx] = Money(amount=results[idx].amount + unit, currency=self.currency)

        return results

    def to_dict(self) -> dict[str, Any]:
        """Serialize Money to dictionary."""
        return {
            "amount": str(self.amount),
            "currency": self.currency.to_dict(),
            "formatted": f"{self.currency.symbol}{self.amount:,.2f}",
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Money":
        """Deserialize dictionary to Money value object."""
        amount = Decimal(str(data["amount"]))
        currency = (
            Currency.from_dict(data["currency"])
            if isinstance(data["currency"], dict)
            else Currency(CurrencyCode(data["currency"]))
        )
        return cls(amount=amount, currency=currency)

    def __str__(self) -> str:
        return f"{self.currency.symbol}{self.amount:,.2f}"
