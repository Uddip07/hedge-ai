"""
Quantity Value Object for the Indian AI Hedge Fund Domain.

Represents non-negative share or contract quantities. Immutable and self-validating.
Supports fractional shares via Decimal.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.domain.exceptions import ValidationError
from packages.domain.utils.math import to_decimal


@dataclass(frozen=True, slots=True)
class Quantity:
    """
    Immutable value object for asset holding and order share quantities.

    Attributes:
        value (Decimal): Share count or contract quantity (>= 0).
    """

    value: Decimal

    def __post_init__(self) -> None:
        dec_val = to_decimal(self.value)
        if dec_val < Decimal("0"):
            raise ValidationError(
                f"Quantity value cannot be negative. Got {dec_val}.",
                context={"value": str(dec_val)},
            )
        object.__setattr__(self, "value", dec_val)

    def is_zero(self) -> bool:
        """Return True if quantity is zero."""
        return self.value == Decimal("0")

    def is_integer(self) -> bool:
        """Return True if quantity is a whole integer number of shares."""
        return self.value == self.value.to_integral_value()

    def __add__(self, other: "Quantity") -> "Quantity":
        return Quantity(value=self.value + other.value)

    def __sub__(self, other: "Quantity") -> "Quantity":
        res = self.value - other.value
        if res < Decimal("0"):
            raise ValidationError("Subtracting quantity results in a negative value.")
        return Quantity(value=res)

    def __mul__(self, scalar: int | float | Decimal) -> "Quantity":
        return Quantity(value=self.value * to_decimal(scalar))

    def __rmul__(self, scalar: int | float | Decimal) -> "Quantity":
        return self.__mul__(scalar)

    def __truediv__(self, scalar: int | float | Decimal) -> "Quantity":
        dec_scalar = to_decimal(scalar)
        if dec_scalar == Decimal("0"):
            raise ValidationError("Cannot divide Quantity by zero.")
        return Quantity(value=self.value / dec_scalar)

    def __lt__(self, other: "Quantity") -> bool:
        return self.value < other.value

    def __le__(self, other: "Quantity") -> bool:
        return self.value <= other.value

    def __gt__(self, other: "Quantity") -> bool:
        return self.value > other.value

    def __ge__(self, other: "Quantity") -> bool:
        return self.value >= other.value

    def to_dict(self) -> dict[str, Any]:
        """Serialize Quantity to dictionary."""
        return {"value": str(self.value), "is_integer": self.is_integer()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Quantity":
        """Deserialize dictionary to Quantity value object."""
        return cls(value=Decimal(str(data["value"])))

    def __str__(self) -> str:
        if self.is_integer():
            return str(int(self.value))
        return f"{self.value:f}"
