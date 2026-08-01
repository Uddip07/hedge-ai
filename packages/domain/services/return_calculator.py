"""
ReturnCalculator Domain Service for the Indian AI Hedge Fund Platform.

Pure domain service calculating total return, annualized return, and Compound Annual Growth Rate (CAGR).
Zero infrastructure dependencies.
"""

from decimal import Decimal

from packages.domain.utils.math import calculate_cagr, calculate_return
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.percentage import Percentage


class ReturnCalculator:
    """
    Stateless domain calculator for portfolio and asset financial returns.
    """

    @staticmethod
    def calculate_simple_return(initial_value: Money, final_value: Money) -> Percentage:
        """
        Calculate simple return percentage from initial to final value.
        """
        if initial_value.amount == Decimal("0"):
            return Percentage(Decimal("0.0"))
        ret_val = calculate_return(initial_value.amount, final_value.amount)
        return Percentage(ret_val)

    @staticmethod
    def calculate_cagr(initial_value: Money, final_value: Money, years: Decimal) -> Percentage:
        """
        Calculate Compound Annual Growth Rate (CAGR).
        """
        if initial_value.amount <= Decimal("0") or years <= Decimal("0"):
            return Percentage(Decimal("0.0"))
        cagr_val = calculate_cagr(initial_value.amount, final_value.amount, years)
        return Percentage(cagr_val)

    @staticmethod
    def calculate_cumulative_return(returns: list[Percentage]) -> Percentage:
        """
        Calculate cumulative compounded return percentage from a series of period returns.
        """
        if not returns:
            return Percentage(Decimal("0.0"))

        cum_factor = Decimal("1.0")
        for r in returns:
            period_ratio = Decimal("1.0") + r.to_ratio()
            cum_factor *= period_ratio

        cum_ret = (cum_factor - Decimal("1.0")) * Decimal("100")
        return Percentage(cum_ret)
