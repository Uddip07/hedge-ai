"""
AllocationPolicy Domain Specification for the Indian AI Hedge Fund Platform.

Encapsulates asset allocation rules (total weight sum <= 1.0, maximum asset weight cap).
Pure domain policy.
"""

from dataclasses import dataclass
from decimal import Decimal

from packages.domain.portfolio.rebalance import RebalancePlan
from packages.domain.value_objects.core.weight import Weight


@dataclass(frozen=True, slots=True)
class AllocationPolicy:
    """
    Immutable domain policy enforcing rebalance allocation plan rules.

    Attributes:
        max_single_asset_weight (Weight): Maximum allowed weight for any single asset (default 15%).
        target_total_weight_max (Decimal): Upper bound for total sum of weights (default 1.0 = 100%).
    """

    max_single_asset_weight: Weight = Weight(Decimal("0.15"))
    target_total_weight_max: Decimal = Decimal("1.0001")

    def validate_rebalance_plan(self, plan: RebalancePlan) -> tuple[bool, list[str]]:
        """
        Validate whether a RebalancePlan satisfies allocation safety limits.

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_policy_violations)
        """
        violations: list[str] = []

        total_w = plan.total_weight_ratio()
        if total_w > self.target_total_weight_max:
            violations.append(
                f"Rebalance plan total weight sum ({total_w:.4f}) exceeds maximum 100% threshold."
            )

        for alloc in plan.allocations:
            if alloc.weight > self.max_single_asset_weight:
                violations.append(
                    f"Asset '{alloc.ticker.full_symbol}' allocation weight ({alloc.weight.ratio * 100:.2f}%) "
                    f"exceeds single asset cap ({self.max_single_asset_weight.ratio * 100:.2f}%)."
                )

        return len(violations) == 0, violations
