"""
AccountBalance and MarginRequirement Value Objects for the Indian AI Hedge Fund Domain.

Represents broker account balance, available buying power, margin usage,
and margin call warning evaluation models. Pure domain value objects.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.domain.enums.system import CurrencyCode
from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.identifiers.currency import Currency


@dataclass(frozen=True, slots=True)
class AccountBalance:
    """
    Immutable value object for brokerage account balances.

    Attributes:
        available_cash (Money): Free available cash.
        used_margin (Money): Margin locked in open positions.
        unrealized_pnl (Money): Total unrealized profit/loss across positions.
        currency (Currency): Account currency (defaults to INR).
    """

    available_cash: Money
    used_margin: Money = Money(Decimal("0.00"))
    unrealized_pnl: Money = Money(Decimal("0.00"))
    currency: Currency = Currency(CurrencyCode.INR)

    def __post_init__(self) -> None:
        if not isinstance(self.available_cash, Money):
            object.__setattr__(self, "available_cash", Money(self.available_cash))
        if not isinstance(self.used_margin, Money):
            object.__setattr__(self, "used_margin", Money(self.used_margin))
        if not isinstance(self.unrealized_pnl, Money):
            object.__setattr__(self, "unrealized_pnl", Money(self.unrealized_pnl))
        if not isinstance(self.currency, Currency):
            object.__setattr__(self, "currency", Currency(self.currency))

    @property
    def total_buying_power(self) -> Money:
        """Return available buying power (available_cash - used_margin + unrealized_pnl)."""
        return self.available_cash - self.used_margin + self.unrealized_pnl

    def to_dict(self) -> dict[str, Any]:
        """Serialize AccountBalance to dictionary."""
        return {
            "available_cash": self.available_cash.to_dict(),
            "used_margin": self.used_margin.to_dict(),
            "unrealized_pnl": self.unrealized_pnl.to_dict(),
            "buying_power": self.total_buying_power.to_dict(),
            "currency": self.currency.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AccountBalance":
        """Deserialize dictionary to AccountBalance."""
        return cls(
            available_cash=Money.from_dict(data["available_cash"]),
            used_margin=(
                Money.from_dict(data["used_margin"])
                if data.get("used_margin")
                else Money(Decimal("0.00"))
            ),
            unrealized_pnl=(
                Money.from_dict(data["unrealized_pnl"])
                if data.get("unrealized_pnl")
                else Money(Decimal("0.00"))
            ),
            currency=(
                Currency.from_dict(data["currency"])
                if data.get("currency")
                else Currency(CurrencyCode.INR)
            ),
        )


@dataclass(frozen=True, slots=True)
class MarginRequirement:
    """
    Immutable value object for position margin parameters.

    Attributes:
        initial_margin (Money): Margin required to open position.
        maintenance_margin (Money): Minimum margin required to maintain open position.
    """

    initial_margin: Money
    maintenance_margin: Money

    def __post_init__(self) -> None:
        if not isinstance(self.initial_margin, Money):
            object.__setattr__(self, "initial_margin", Money(self.initial_margin))
        if not isinstance(self.maintenance_margin, Money):
            object.__setattr__(self, "maintenance_margin", Money(self.maintenance_margin))

        if self.maintenance_margin > self.initial_margin:
            raise ValidationError("Maintenance margin cannot exceed initial margin requirement.")

    def is_margin_call(self, available_equity: Money) -> bool:
        """Return True if available account equity drops below maintenance margin."""
        return available_equity < self.maintenance_margin

    def to_dict(self) -> dict[str, Any]:
        """Serialize MarginRequirement to dictionary."""
        return {
            "initial_margin": self.initial_margin.to_dict(),
            "maintenance_margin": self.maintenance_margin.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarginRequirement":
        """Deserialize dictionary to MarginRequirement."""
        return cls(
            initial_margin=Money.from_dict(data["initial_margin"]),
            maintenance_margin=Money.from_dict(data["maintenance_margin"]),
        )
