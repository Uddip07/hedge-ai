"""
SectorWeight Value Object for the Indian AI Hedge Fund Domain.

Represents portfolio allocation weight assigned to a MarketSegment (e.g., LARGE_CAP, IT, BANKING).
Immutable and self-validating.
"""

from dataclasses import dataclass
from typing import Any

from packages.domain.enums.market import MarketSegment
from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.core.weight import Weight


@dataclass(frozen=True, slots=True)
class SectorWeight:
    """
    Immutable value object for sector exposure weight bounds.

    Attributes:
        sector (MarketSegment): Market segment enum.
        weight (Weight): Sector weight value object.
    """

    sector: MarketSegment
    weight: Weight

    def __post_init__(self) -> None:
        if not isinstance(self.sector, MarketSegment):
            try:
                object.__setattr__(self, "sector", MarketSegment(self.sector))
            except ValueError as exc:
                raise ValidationError(
                    f"Invalid MarketSegment for SectorWeight: '{self.sector}'."
                ) from exc
        if not isinstance(self.weight, Weight):
            raise ValidationError("SectorWeight must bind a valid Weight instance.")

    def to_dict(self) -> dict[str, Any]:
        """Serialize SectorWeight to dictionary."""
        return {
            "sector": self.sector.value,
            "weight": self.weight.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SectorWeight":
        """Deserialize dictionary to SectorWeight value object."""
        sector = MarketSegment(data["sector"])
        weight = Weight.from_dict(data["weight"])
        return cls(sector=sector, weight=weight)

    def __str__(self) -> str:
        return f"{self.sector.value}: {self.weight}"
