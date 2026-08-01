"""
PortfolioCalculator Domain Service for the Indian AI Hedge Fund Platform.

Pure domain service calculating total portfolio valuation, holding weights,
and sector concentration metrics. Zero infrastructure dependencies.
"""

from decimal import Decimal

from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.weight import Weight


class PortfolioCalculator:
    """
    Stateless domain calculator for portfolio aggregate state and metrics.
    """

    @staticmethod
    def calculate_total_equity(portfolio: Portfolio) -> Money:
        """
        Calculate total equity valuation (cash + market value of all holdings).
        """
        return portfolio.total_equity()

    @staticmethod
    def calculate_holding_weights(portfolio: Portfolio) -> dict[str, Weight]:
        """
        Calculate position weighting ratio for every holding in portfolio.
        """
        tot_eq = portfolio.total_equity()
        if tot_eq.is_zero() or tot_eq.is_negative():
            return {sym: Weight(Decimal("0.0")) for sym in portfolio.holdings}

        weights: dict[str, Weight] = {}
        for sym, holding in portfolio.holdings.items():
            w_ratio = holding.current_value.amount / tot_eq.amount
            weights[sym] = Weight(w_ratio)

        return weights

    @staticmethod
    def calculate_unrealized_pnl(portfolio: Portfolio) -> Money:
        """
        Calculate total unrealized PnL across all open portfolio holdings.
        """
        base_curr = portfolio.cash_balance.currency
        if not portfolio.holdings:
            return Money(Decimal("0.00"), currency=base_curr)

        total_pnl = Money(Decimal("0.00"), currency=base_curr)
        for holding in portfolio.holdings.values():
            total_pnl = total_pnl + holding.unrealized_pnl
        return total_pnl
