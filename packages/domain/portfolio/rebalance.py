"""
RebalancePlan Value Object for the Indian AI Hedge Fund Platform.

Represents a portfolio rebalance instruction set with asset weight allocations.
Pure domain model with zero infrastructure dependencies.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from packages.domain.enums.portfolio import AllocationMethod
from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.core.allocation import Allocation
from packages.domain.value_objects.identifiers import PortfolioId
from packages.domain.value_objects.temporal.timestamps import Timestamp

__all__ = ["RebalancePlan", "Allocation"]


@dataclass(frozen=True, slots=True)
class RebalancePlan:
    """
    Immutable value object defining target asset rebalance weights.

    Attributes:
        portfolio_id (PortfolioId): ID of the portfolio to rebalance.
        method (AllocationMethod): Allocation weighting strategy used.
        allocations (List[Allocation]): Target asset allocations.
        created_at (Timestamp): Plan creation timestamp.
    """

    portfolio_id: PortfolioId
    method: AllocationMethod
    allocations: list[Allocation] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=Timestamp.now_utc)

    def __post_init__(self) -> None:
        if not isinstance(self.portfolio_id, PortfolioId):
            object.__setattr__(self, "portfolio_id", PortfolioId(self.portfolio_id))
        if not isinstance(self.method, AllocationMethod):
            object.__setattr__(self, "method", AllocationMethod(self.method))
        if not isinstance(self.created_at, Timestamp):
            object.__setattr__(self, "created_at", Timestamp(self.created_at))

        if not self.allocations:
            raise ValidationError("RebalancePlan must contain at least one asset Allocation.")

    def total_weight_ratio(self) -> Decimal:
        """Calculate total sum of allocation weight ratios."""
        return sum((alloc.weight.ratio for alloc in self.allocations), Decimal("0"))

    def is_valid(self) -> bool:
        """Return True if total allocation weight <= 1.0 (100%)."""
        return self.total_weight_ratio() <= Decimal("1.0001")

    def to_dict(self) -> dict[str, Any]:
        """Serialize RebalancePlan to dictionary."""
        return {
            "portfolio_id": self.portfolio_id.to_dict(),
            "method": self.method.value,
            "allocations": [a.to_dict() for a in self.allocations],
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RebalancePlan":
        """Deserialize dictionary to RebalancePlan."""
        allocations = [Allocation.from_dict(a) for a in data.get("allocations", [])]
        return cls(
            portfolio_id=PortfolioId.from_dict(data["portfolio_id"]),
            method=AllocationMethod(data["method"]),
            allocations=allocations,
            created_at=Timestamp.from_isoformat(data["created_at"]),
        )
