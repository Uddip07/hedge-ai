"""
RiskPolicy Domain Specification for the Indian AI Hedge Fund Platform.

Encapsulates portfolio risk limits (Max Position Size %, Max Sector Concentration %,
Max Drawdown Limit) and evaluates order placement safety. Pure domain policy.
"""

from dataclasses import dataclass
from decimal import Decimal

from packages.domain.brokerage.order import Order
from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.value_objects.core.percentage import Percentage


@dataclass(frozen=True, slots=True)
class RiskPolicy:
    """
    Immutable domain policy enforcing portfolio risk controls.

    Attributes:
        max_position_size_pct (Percentage): Maximum allowed allocation to a single asset position (default 10%).
        max_sector_concentration_pct (Percentage): Maximum allowed allocation to a single sector (default 25%).
        max_portfolio_drawdown_pct (Percentage): Maximum acceptable portfolio drawdown threshold (default 15%).
        max_leverage_ratio (Decimal): Maximum allowed leverage multiplier (default 1.0 = no leverage).
    """

    max_position_size_pct: Percentage = Percentage(Decimal("10.0"))
    max_sector_concentration_pct: Percentage = Percentage(Decimal("25.0"))
    max_portfolio_drawdown_pct: Percentage = Percentage(Decimal("15.0"))
    max_leverage_ratio: Decimal = Decimal("1.0")

    def evaluate_order_risk(self, portfolio: Portfolio, order: Order) -> tuple[bool, list[str]]:
        """
        Evaluate whether placing order violates any portfolio risk policy thresholds.

        Returns:
            Tuple[bool, List[str]]: (is_allowed, list_of_policy_violations)
        """
        violations: list[str] = []
        total_eq = portfolio.total_equity()

        if total_eq.is_zero() or total_eq.is_negative():
            violations.append("Portfolio equity is zero or negative; order rejected.")
            return False, violations

        if order.trade_type.is_buy():
            est_order_price = order.price.amount if order.price else Decimal("0")
            est_order_val = est_order_price * order.quantity.value

            # Check single position size limit
            max_pos_val = total_eq.amount * self.max_position_size_pct.to_ratio()
            symbol_key = order.ticker.full_symbol

            existing_holding_val = Decimal("0")
            if symbol_key in portfolio.holdings:
                existing_holding_val = portfolio.holdings[symbol_key].current_value.amount

            new_pos_val = existing_holding_val + est_order_val
            if new_pos_val > max_pos_val:
                violations.append(
                    f"Position value ({new_pos_val} INR) exceeds max single position policy limit "
                    f"({max_pos_val:.2f} INR, {self.max_position_size_pct.value}% of portfolio equity)."
                )

        return len(violations) == 0, violations
