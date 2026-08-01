"""
SharpeCalculator Domain Service for the Indian AI Hedge Fund Platform.

Pure domain service calculating risk-adjusted performance metrics:
Sharpe Ratio and Sortino Ratio (downside risk adjusted). Zero infrastructure dependencies.
"""

from decimal import Decimal

from packages.domain.utils.math import to_decimal
from packages.domain.value_objects.metrics.ratios import SharpeRatio, SortinoRatio


def _calc_std_dev(returns: list[Decimal]) -> Decimal:
    """Calculate sample standard deviation of return series."""
    if len(returns) < 2:
        return Decimal("0.0")
    mean = sum(returns) / Decimal(str(len(returns)))
    variance = sum((x - mean) ** 2 for x in returns) / Decimal(str(len(returns) - 1))
    return variance.sqrt()


class SharpeCalculator:
    """
    Stateless domain calculator for risk-adjusted return ratios.
    """

    @staticmethod
    def calculate_sharpe_ratio(
        period_returns: list[Decimal],
        risk_free_rate_annual: Decimal = Decimal("0.07"),  # 7% Indian RBI repo/g-sec rate
        periods_per_year: int = 252,
    ) -> SharpeRatio:
        """
        Calculate annualized Sharpe Ratio.
        """
        if not period_returns or len(period_returns) < 2:
            return SharpeRatio(Decimal("0.0"))

        dec_returns = [to_decimal(r) for r in period_returns]
        rf_period = risk_free_rate_annual / Decimal(str(periods_per_year))

        excess_returns = [r - rf_period for r in dec_returns]
        mean_excess = sum(excess_returns) / Decimal(str(len(excess_returns)))

        sd = _calc_std_dev(dec_returns)
        if sd == Decimal("0"):
            return SharpeRatio(Decimal("0.0"))

        ann_factor = Decimal(str(periods_per_year)).sqrt()
        sharpe_val = (mean_excess / sd) * ann_factor
        return SharpeRatio(sharpe_val)

    @staticmethod
    def calculate_sortino_ratio(
        period_returns: list[Decimal],
        risk_free_rate_annual: Decimal = Decimal("0.07"),
        periods_per_year: int = 252,
    ) -> SortinoRatio:
        """
        Calculate annualized Sortino Ratio (downside deviation adjusted).
        """
        if not period_returns or len(period_returns) < 2:
            return SortinoRatio(Decimal("0.0"))

        dec_returns = [to_decimal(r) for r in period_returns]
        rf_period = risk_free_rate_annual / Decimal(str(periods_per_year))

        excess_returns = [r - rf_period for r in dec_returns]
        mean_excess = sum(excess_returns) / Decimal(str(len(excess_returns)))

        # Downside deviation: only negative excess returns
        downside_diffs = [min(Decimal("0.0"), er) ** 2 for er in excess_returns]
        downside_variance = sum(downside_diffs) / Decimal(str(len(downside_diffs)))
        downside_dev = downside_variance.sqrt()

        if downside_dev == Decimal("0"):
            return SortinoRatio(Decimal("0.0"))

        ann_factor = Decimal(str(periods_per_year)).sqrt()
        sortino_val = (mean_excess / downside_dev) * ann_factor
        return SortinoRatio(sortino_val)
