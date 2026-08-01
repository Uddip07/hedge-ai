"""
Unit tests for Domain Calculators and Services (ReturnCalculator, DrawdownCalculator, SharpeCalculator,
RiskCalculator, PortfolioCalculator, ConsensusCalculator, RecommendationAggregator).
"""

import unittest
from decimal import Decimal

from packages.domain.enums.ai import AgentType
from packages.domain.enums.portfolio import PortfolioType
from packages.domain.enums.research import RecommendationType
from packages.domain.portfolio.holding import Holding
from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.research.consensus import AgentOpinion
from packages.domain.services import (
    ConsensusCalculator,
    DrawdownCalculator,
    PortfolioCalculator,
    RecommendationAggregator,
    ReturnCalculator,
    RiskCalculator,
    SharpeCalculator,
)
from packages.domain.value_objects.core import Money, Price, Quantity
from packages.domain.value_objects.identifiers import Ticker
from packages.domain.value_objects.metrics import ConfidenceScore


class TestCalculatorsDomain(unittest.TestCase):
    """Test suite for domain calculator services."""

    def test_return_calculator(self):
        v1 = Money(Decimal("100000.00"))
        v2 = Money(Decimal("120000.00"))

        ret = ReturnCalculator.calculate_simple_return(v1, v2)
        self.assertEqual(ret.value, Decimal("20.0"))

        cagr = ReturnCalculator.calculate_cagr(v1, v2, years=Decimal("2.0"))
        self.assertAlmostEqual(float(cagr.value), 9.54, delta=0.1)

    def test_drawdown_calculator(self):
        curr = Money(Decimal("80000.00"))
        peak = Money(Decimal("100000.00"))

        dd = DrawdownCalculator.calculate_current_drawdown(curr, peak)
        self.assertEqual(dd.value, Decimal("20.0000"))  # 20% drawdown

        series = [
            Money(Decimal("100.00")),
            Money(Decimal("120.00")),
            Money(Decimal("90.00")),
            Money(Decimal("110.00")),
        ]
        max_dd, duration = DrawdownCalculator.calculate_max_drawdown(series)
        self.assertEqual(max_dd.value, Decimal("25.0000"))  # 120 -> 90 = 25%
        self.assertEqual(duration, 2)

    def test_sharpe_and_sortino_calculator(self):
        returns = [Decimal("0.02"), Decimal("-0.01"), Decimal("0.03"), Decimal("0.015")]

        sharpe = SharpeCalculator.calculate_sharpe_ratio(
            returns, risk_free_rate_annual=Decimal("0.05")
        )
        self.assertIsNotNone(sharpe)

        sortino = SharpeCalculator.calculate_sortino_ratio(
            returns, risk_free_rate_annual=Decimal("0.05")
        )
        self.assertIsNotNone(sortino)

    def test_risk_calculator_volatility_and_var(self):
        returns = [Decimal("0.01"), Decimal("-0.02"), Decimal("0.015"), Decimal("-0.01")]
        vol = RiskCalculator.calculate_annualized_volatility(returns)
        self.assertGreater(vol.value, Decimal("0"))

        portfolio_val = Money(Decimal("1000000.00"))
        var_amt, cvar_amt = RiskCalculator.calculate_historical_var_cvar(returns, portfolio_val)
        self.assertGreaterEqual(var_amt.amount, Decimal("0"))
        self.assertGreaterEqual(cvar_amt.amount, Decimal("0"))

    def test_portfolio_calculator(self):
        port = Portfolio(name="Test Portfolio", portfolio_type=PortfolioType.PAPER)
        port.deposit_cash(Money(Decimal("50000.00")))

        holding = Holding(
            ticker=Ticker("RELIANCE.NSE"),
            quantity=Quantity(Decimal("10")),
            average_buy_price=Price.from_amount("2000"),
            current_price=Price.from_amount("2500"),
        )
        port.holdings["RELIANCE.NSE"] = holding

        tot_eq = PortfolioCalculator.calculate_total_equity(port)
        self.assertEqual(tot_eq.amount, Decimal("75000.00"))  # 50k cash + 25k stock

        weights = PortfolioCalculator.calculate_holding_weights(port)
        self.assertAlmostEqual(float(weights["RELIANCE.NSE"].ratio), 0.333, delta=0.01)

        unrealized = PortfolioCalculator.calculate_unrealized_pnl(port)
        self.assertEqual(unrealized.amount, Decimal("5000.00"))

    def test_consensus_and_recommendation_aggregator(self):
        t = Ticker("INFY.NSE")
        op1 = AgentOpinion(
            agent_type=AgentType.FUNDAMENTAL,
            recommendation=RecommendationType.STRONG_BUY,
            reasoning="Strong earnings growth.",
            confidence=ConfidenceScore(Decimal("0.90")),
        )
        op2 = AgentOpinion(
            agent_type=AgentType.QUANT,
            recommendation=RecommendationType.BUY,
            reasoning="Positive momentum factor.",
            confidence=ConfidenceScore(Decimal("0.80")),
        )

        rec_score, conf_score = ConsensusCalculator.calculate_consensus_score([op1, op2])
        self.assertGreater(rec_score.value, Decimal("0.5"))

        final_rec = RecommendationAggregator.aggregate(
            ticker=t,
            opinions=[op1, op2],
        )
        self.assertIn(
            final_rec.recommendation, {RecommendationType.STRONG_BUY, RecommendationType.BUY}
        )


if __name__ == "__main__":
    unittest.main()
