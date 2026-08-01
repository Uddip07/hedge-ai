"""
DrawdownCalculator Domain Service for the Indian AI Hedge Fund Platform.

Pure domain service calculating current drawdown, max drawdown, and drawdown duration tracking.
Zero infrastructure dependencies.
"""

from decimal import Decimal

from packages.domain.utils.math import calculate_drawdown
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.metrics.ratios import Drawdown


class DrawdownCalculator:
    """
    Stateless domain calculator for peak-to-trough drawdowns and duration tracking.
    """

    @staticmethod
    def calculate_current_drawdown(
        current_equity: Money,
        peak_equity: Money,
    ) -> Drawdown:
        """
        Calculate current drawdown percentage from peak.
        """
        dd_val = calculate_drawdown(current_equity.amount, peak_equity.amount)
        return Drawdown.from_value(dd_val)

    @staticmethod
    def calculate_max_drawdown(
        equity_series: list[Money],
    ) -> tuple[Drawdown, int]:
        """
        Calculate maximum drawdown percentage and maximum drawdown duration (periods) from equity time-series.

        Returns:
            tuple[Drawdown, int]: (MaxDrawdown ValueObject, MaxDrawdownDuration in periods).
        """
        if not equity_series or len(equity_series) < 2:
            return Drawdown.from_value(Decimal("0.0")), 0

        peak = equity_series[0].amount
        max_dd = Decimal("0.0")
        max_duration = 0
        current_duration = 0

        for eq in equity_series:
            val = eq.amount
            if val > peak:
                peak = val
                current_duration = 0
            else:
                dd = calculate_drawdown(val, peak)
                if dd > max_dd:
                    max_dd = dd
                current_duration += 1
                if current_duration > max_duration:
                    max_duration = current_duration

        return Drawdown.from_value(max_dd), max_duration
