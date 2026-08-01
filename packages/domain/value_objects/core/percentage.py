"""
Percentage Value Object for the Indian AI Hedge Fund Domain.

Represents a percentage value (e.g. 15.5 for 15.5%). Immutable and self-validating.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.domain.exceptions import ValidationError
from packages.domain.utils.math import round_currency, to_decimal


@dataclass(frozen=True, slots=True)
class Percentage:
    """
    Immutable value object for percentage values (0 to 100 or unbounded).

    Attributes:
        value (Decimal): Percentage number (e.g., Decimal('15.5') for 15.5%).
    """

    value: Decimal

    def __post_init__(self) -> None:
        dec_val = to_decimal(self.value)
        object.__setattr__(self, "value", dec_val)

    @classmethod
    def from_ratio(cls, ratio: int | float | str | Decimal) -> "Percentage":
        """Construct Percentage from decimal ratio (e.g., 0.155 -> 15.5%)."""
        dec_ratio = to_decimal(ratio)
        return cls(value=dec_ratio * Decimal("100"))

    def to_ratio(self) -> Decimal:
        """Convert percentage to ratio (e.g., 15.5% -> Decimal('0.155'))."""
        return self.value / Decimal("100")

    def clamp(
        self,
        min_pct: int | float | Decimal = Decimal("0"),
        max_pct: int | float | Decimal = Decimal("100"),
    ) -> "Percentage":
        """Return a new Percentage clamped within [min_pct, max_pct]."""
        min_dec = to_decimal(min_pct)
        max_dec = to_decimal(max_pct)
        clamped = max(min_dec, min(self.value, max_dec))
        return Percentage(value=clamped)

    def normalize(self) -> "Percentage":
        """Return Percentage normalized to [0, 100]."""
        return self.clamp(Decimal("0"), Decimal("100"))

    def rounded(self, decimals: int = 2) -> "Percentage":
        """Return rounded Percentage."""
        return Percentage(value=round_currency(self.value, decimals=decimals))

    def __add__(self, other: "Percentage") -> "Percentage":
        return Percentage(value=self.value + other.value)

    def __sub__(self, other: "Percentage") -> "Percentage":
        return Percentage(value=self.value - other.value)

    def __mul__(self, scalar: int | float | Decimal) -> "Percentage":
        return Percentage(value=self.value * to_decimal(scalar))

    def __rmul__(self, scalar: int | float | Decimal) -> "Percentage":
        return self.__mul__(scalar)

    def __truediv__(self, scalar: int | float | Decimal) -> "Percentage":
        dec_scalar = to_decimal(scalar)
        if dec_scalar == Decimal("0"):
            raise ValidationError("Cannot divide Percentage by zero.")
        return Percentage(value=self.value / dec_scalar)

    def __lt__(self, other: "Percentage") -> bool:
        return self.value < other.value

    def __le__(self, other: "Percentage") -> bool:
        return self.value <= other.value

    def __gt__(self, other: "Percentage") -> bool:
        return self.value > other.value

    def __ge__(self, other: "Percentage") -> bool:
        return self.value >= other.value

    def to_dict(self) -> dict[str, Any]:
        """Serialize Percentage to dictionary."""
        return {
            "value": str(self.value),
            "ratio": str(self.to_ratio()),
            "formatted": f"{self.value:.2f}%",
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Percentage":
        """Deserialize dictionary to Percentage value object."""
        return cls(value=Decimal(str(data["value"])))

    def __str__(self) -> str:
        return f"{self.value:.2f}%"
