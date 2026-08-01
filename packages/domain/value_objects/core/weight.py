"""
Weight Value Object for the Indian AI Hedge Fund Domain.

Represents a portfolio position weighting factor as a Decimal ratio in range [0.0, 1.0].
Immutable and self-validating.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.domain.exceptions import ValidationError
from packages.domain.utils.math import to_decimal
from packages.domain.value_objects.core.percentage import Percentage


@dataclass(frozen=True, slots=True)
class Weight:
    """
    Immutable value object for position weight ratios (0.0 to 1.0).

    Attributes:
        ratio (Decimal): Weight decimal ratio (e.g., Decimal('0.15') for 15%).
    """

    ratio: Decimal

    def __post_init__(self) -> None:
        dec_ratio = to_decimal(self.ratio)
        if dec_ratio < Decimal("0") or dec_ratio > Decimal("1"):
            raise ValidationError(
                f"Weight ratio must be between 0.0 and 1.0 (got {dec_ratio}).",
                context={"ratio": str(dec_ratio)},
            )
        object.__setattr__(self, "ratio", dec_ratio)

    @classmethod
    def from_percentage(cls, pct: Percentage) -> "Weight":
        """Construct Weight from Percentage value object."""
        return cls(ratio=pct.to_ratio())

    def as_percentage(self) -> Percentage:
        """Convert weight ratio to Percentage value object."""
        return Percentage.from_ratio(self.ratio)

    def is_zero(self) -> bool:
        """Return True if weight is 0."""
        return self.ratio == Decimal("0")

    def __add__(self, other: "Weight") -> "Weight":
        return Weight(ratio=self.ratio + other.ratio)

    def __sub__(self, other: "Weight") -> "Weight":
        return Weight(ratio=self.ratio - other.ratio)

    def __mul__(self, scalar: int | float | Decimal) -> "Weight":
        return Weight(ratio=self.ratio * to_decimal(scalar))

    def __rmul__(self, scalar: int | float | Decimal) -> "Weight":
        return self.__mul__(scalar)

    def __lt__(self, other: "Weight") -> bool:
        return self.ratio < other.ratio

    def __le__(self, other: "Weight") -> bool:
        return self.ratio <= other.ratio

    def __gt__(self, other: "Weight") -> bool:
        return self.ratio > other.ratio

    def __ge__(self, other: "Weight") -> bool:
        return self.ratio >= other.ratio

    def to_dict(self) -> dict[str, Any]:
        """Serialize Weight to dictionary."""
        return {
            "ratio": str(self.ratio),
            "percentage": self.as_percentage().to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Weight":
        """Deserialize dictionary to Weight value object."""
        return cls(ratio=Decimal(str(data["ratio"])))

    def __str__(self) -> str:
        return f"{self.as_percentage()}"
