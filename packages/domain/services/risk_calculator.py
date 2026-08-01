"""
RiskCalculator Domain Service for the Indian AI Hedge Fund Platform.

Pure domain service calculating annualized volatility, Historical VaR (95%),
and Expected Shortfall (CVaR). Zero infrastructure dependencies.
"""

from decimal import Decimal

from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.services.sharpe_calculator import _calc_std_dev
from packages.domain.utils.validation import to_decimal
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.metrics.ratios import Volatility


class RiskCalculator:
    """
    Stateless domain calculator for portfolio and return series risk metrics.
    """

    @staticmethod
    def calculate_annualized_volatility(
        period_returns: list[Decimal],
        periods_per_year: int = 252,
    ) -> Volatility:
        """
        Calculate annualized volatility (standard deviation * sqrt(periods_per_year)).
        """
        if not period_returns or len(period_returns) < 2:
            return Volatility.from_value(Decimal("0.0"))

        dec_returns = [to_decimal(r) for r in period_returns]
        std_dev = _calc_std_dev(dec_returns)
        ann_factor = Decimal(str(periods_per_year)).sqrt()
        ann_vol = std_dev * ann_factor * Decimal("100")
        return Volatility.from_value(ann_vol)

    @staticmethod
    def calculate_historical_var_cvar(
        returns: list[Decimal],
        portfolio_value: Money,
        confidence_level: Decimal = Decimal("0.95"),
    ) -> tuple[Money, Money]:
        """
        Calculate Historical Value at Risk (VaR) and Conditional VaR (CVaR / Expected Shortfall).
        """
        if not returns:
            zero_money = Money(Decimal("0.00"), currency=portfolio_value.currency)
            return zero_money, zero_money

        sorted_returns = sorted([to_decimal(r) for r in returns])
        n = len(sorted_returns)

        # Index corresponding to 1 - confidence_level quantile
        cutoff_idx = int((Decimal("1.0") - confidence_level) * Decimal(str(n)))
        cutoff_idx = max(0, min(cutoff_idx, n - 1))

        var_pct = abs(sorted_returns[cutoff_idx])
        var_amount = portfolio_value.amount * var_pct
        var_money = Money(var_amount, currency=portfolio_value.currency)

        # Tail returns worse than VaR
        tail_returns = sorted_returns[: cutoff_idx + 1]
        cvar_pct = (
            abs(sum(tail_returns) / Decimal(str(len(tail_returns)))) if tail_returns else var_pct
        )
        cvar_amount = portfolio_value.amount * cvar_pct
        cvar_money = Money(cvar_amount, currency=portfolio_value.currency)

        return var_money, cvar_money

    @staticmethod
    def calculate_portfolio_var(
        portfolio: Portfolio,
        asset_returns: dict[str, list[Decimal]],
    ) -> Money:
        """
        Calculate aggregate portfolio VaR using holdings weighting.
        """
        tot_eq = portfolio.total_equity()
        if tot_eq.is_zero() or not asset_returns:
            return Money(Decimal("0.00"), currency=portfolio.cash_balance.currency)

        # Aggregate weighted return series across holdings
        sample_len = min(len(ret) for ret in asset_returns.values())
        if sample_len == 0:
            return Money(Decimal("0.00"), currency=portfolio.cash_balance.currency)

        port_returns: list[Decimal] = [Decimal("0.0") for _ in range(sample_len)]

        for sym, ret_series in asset_returns.items():
            if sym in portfolio.holdings:
                w = (
                    portfolio.holdings[sym].current_value.amount / tot_eq.amount
                    if tot_eq.amount > Decimal("0")
                    else Decimal("0")
                )
                for i in range(sample_len):
                    port_returns[i] += ret_series[i] * w

        var_money, _ = RiskCalculator.calculate_historical_var_cvar(port_returns, tot_eq)
        return var_money
