"""
PortfolioPolicy Domain Specification for the Indian AI Hedge Fund Platform.

Encapsulates portfolio-level capacity limits (minimum cash buffer reserve %,
maximum holdings count). Pure domain policy.
"""

from dataclasses import dataclass
from decimal import Decimal

from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.value_objects.core.percentage import Percentage


@dataclass(frozen=True, slots=True)
class PortfolioPolicy:
    """
    Immutable domain policy enforcing portfolio operational boundaries.

    Attributes:
        min_cash_buffer_pct (Percentage): Required minimum unallocated cash buffer reserve (default 2%).
        max_holdings_count (int): Maximum allowed distinct asset holdings in portfolio (default 50).
    """

    min_cash_buffer_pct: Percentage = Percentage(Decimal("2.0"))
    max_holdings_count: int = 50

    def validate_portfolio_limits(self, portfolio: Portfolio) -> tuple[bool, list[str]]:
        """
        Evaluate portfolio health against cash reserve and holding capacity limits.

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_policy_violations)
        """
        violations: list[str] = []
        total_eq = portfolio.total_equity()

        if total_eq.is_zero() or total_eq.is_negative():
            violations.append("Portfolio equity is zero or negative.")
            return False, violations

        cash_ratio = portfolio.cash_balance.amount / total_eq.amount
        if cash_ratio < self.min_cash_buffer_pct.to_ratio():
            violations.append(
                f"Portfolio cash ratio ({cash_ratio * 100:.2f}%) is below minimum required cash buffer "
                f"({self.min_cash_buffer_pct.value}%)."
            )

        if len(portfolio.holdings) > self.max_holdings_count:
            violations.append(
                f"Holdings count ({len(portfolio.holdings)}) exceeds maximum allowed limit ({self.max_holdings_count})."
            )

        return len(violations) == 0, violations
