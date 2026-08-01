"""
Unit tests for Domain Policies across Risk, Execution, Portfolio, Allocation, Dividend, Tax, and Research.
"""

import unittest
from datetime import date
from decimal import Decimal

from packages.domain.brokerage.order import Order
from packages.domain.enums.ai import AgentType
from packages.domain.enums.market import MarketSession
from packages.domain.enums.portfolio import AllocationMethod, PortfolioType, TaxType
from packages.domain.enums.research import RecommendationType
from packages.domain.enums.trading import AssetType, OrderType, TradeType
from packages.domain.market.asset import Asset
from packages.domain.policies import (
    AllocationPolicy,
    DividendPolicy,
    ExecutionPolicy,
    PortfolioPolicy,
    ResearchPolicy,
    RiskPolicy,
    TaxPolicy,
)
from packages.domain.portfolio.holding import Holding
from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.portfolio.rebalance import Allocation, RebalancePlan
from packages.domain.research.consensus import AgentOpinion
from packages.domain.research.report import ResearchReport
from packages.domain.value_objects.core import Money, Percentage, Price, Quantity, Weight
from packages.domain.value_objects.identifiers import BrokerId, PortfolioId, Ticker
from packages.domain.value_objects.metrics import ConfidenceScore


class TestPoliciesDomain(unittest.TestCase):
    """Test suite for domain policy implementations."""

    def test_risk_policy_evaluation(self):
        policy = RiskPolicy(max_position_size_pct=Percentage(Decimal("10.0")))
        port = Portfolio(name="Main Portfolio", portfolio_type=PortfolioType.PAPER)
        port.deposit_cash(Money(Decimal("100000.00")))
        b_id = BrokerId.generate()

        # Order within limits: 10 shares * 500 = 5000 INR (5% of 100k)
        valid_order = Order(
            broker_account_id=b_id,
            portfolio_id=port.id,
            ticker=Ticker("RELIANCE.NSE"),
            order_type=OrderType.LIMIT,
            trade_type=TradeType.BUY,
            quantity=Quantity(Decimal("10")),
            price=Price.from_amount("500"),
        )
        is_ok, violations = policy.evaluate_order_risk(port, valid_order)
        self.assertTrue(is_ok)
        self.assertEqual(len(violations), 0)

        # Order exceeding limits: 300 shares * 500 = 150000 INR (>10% limit)
        excess_order = Order(
            broker_account_id=b_id,
            portfolio_id=port.id,
            ticker=Ticker("RELIANCE.NSE"),
            order_type=OrderType.LIMIT,
            trade_type=TradeType.BUY,
            quantity=Quantity(Decimal("300")),
            price=Price.from_amount("500"),
        )
        is_ok, violations = policy.evaluate_order_risk(port, excess_order)
        self.assertFalse(is_ok)
        self.assertIn("exceeds max single position policy limit", violations[0])

    def test_execution_policy_validation(self):
        policy = ExecutionPolicy(max_price_collar_pct=Decimal("5.0"))
        asset = Asset(
            name="Reliance Industries",
            ticker=Ticker("RELIANCE.NSE"),
            asset_type=AssetType.EQUITY,
            tick_size=Decimal("0.05"),
            lot_size=1,
        )
        order = Order(
            broker_account_id=BrokerId.generate(),
            portfolio_id=PortfolioId.generate(),
            ticker=Ticker("RELIANCE.NSE"),
            order_type=OrderType.LIMIT,
            trade_type=TradeType.BUY,
            quantity=Quantity(Decimal("10")),
            price=Price.from_amount("2500"),
        )

        ref_price = Price.from_amount("2500")
        is_ok, violations = policy.validate_execution_rules(
            asset, order, MarketSession.NORMAL, reference_price=ref_price
        )
        self.assertTrue(is_ok)

        # Unallowed session failure
        is_ok, violations = policy.validate_execution_rules(
            asset, order, MarketSession.POST_MARKET, reference_price=ref_price
        )
        self.assertFalse(is_ok)

    def test_portfolio_policy_cash_buffer(self):
        policy = PortfolioPolicy(min_cash_buffer_pct=Percentage(Decimal("5.0")))
        port = Portfolio(name="Low Cash Portfolio", portfolio_type=PortfolioType.LIVE)
        port.deposit_cash(Money(Decimal("1000.00")))

        # Add large holding to reduce cash ratio
        holding = Holding(
            ticker=Ticker("TCS.NSE"),
            quantity=Quantity(Decimal("100")),
            average_buy_price=Price.from_amount("3000"),
            current_price=Price.from_amount("3000"),
        )
        port.holdings["TCS.NSE"] = holding

        is_ok, violations = policy.validate_portfolio_limits(port)
        self.assertFalse(is_ok)
        self.assertIn("is below minimum required cash buffer", violations[0])

    def test_allocation_policy_validation(self):
        policy = AllocationPolicy(max_single_asset_weight=Weight(Decimal("0.20")))
        alloc1 = Allocation(ticker=Ticker("RELIANCE.NSE"), weight=Weight(Decimal("0.25")))
        plan = RebalancePlan(
            portfolio_id=PortfolioId.generate(),
            allocations=[alloc1],
            method=AllocationMethod.EQUAL_WEIGHT,
        )

        is_ok, violations = policy.validate_rebalance_plan(plan)
        self.assertFalse(is_ok)
        self.assertIn("exceeds single asset cap", violations[0])

    def test_dividend_policy_tds_calculation(self):
        policy = DividendPolicy(tds_withholding_rate_pct=Decimal("10.0"))
        holding = Holding(
            ticker=Ticker("INFY.NSE"),
            quantity=Quantity(Decimal("100")),
            average_buy_price=Price.from_amount("1400"),
            current_price=Price.from_amount("1400"),
        )

        gross, tds, net = policy.calculate_net_dividend(
            holding=holding,
            dividend_per_share=Price.from_amount("20.00"),
            record_date=date(2026, 6, 1),
            holding_as_of_date=date(2026, 5, 20),
        )

        self.assertEqual(gross.amount, Decimal("2000.00"))
        self.assertEqual(tds.amount, Decimal("200.00"))
        self.assertEqual(net.amount, Decimal("1800.00"))

    def test_tax_policy_calculations(self):
        policy = TaxPolicy()

        # STT on sell trade
        stt = policy.calculate_trade_stt(TradeType.SELL, Money(Decimal("100000.00")))
        self.assertEqual(stt.amount, Decimal("100.00"))  # 0.1% of 100k

        # STCG (<365 days)
        taxes = policy.calculate_capital_gains_tax(
            Money(Decimal("10000.00")), holding_period_days=180
        )
        self.assertEqual(taxes[TaxType.STCG].amount, Decimal("2000.00"))  # 20%
        self.assertEqual(taxes[TaxType.LTCG].amount, Decimal("0.00"))

        # LTCG (>365 days)
        taxes_ltcg = policy.calculate_capital_gains_tax(
            Money(Decimal("10000.00")), holding_period_days=400
        )
        self.assertEqual(taxes_ltcg[TaxType.LTCG].amount, Decimal("1250.00"))  # 12.5%

    def test_research_policy_quorum_and_confidence(self):
        policy = ResearchPolicy(
            min_agent_quorum=2, min_confidence_threshold=ConfidenceScore(Decimal("0.80"))
        )
        report = ResearchReport(ticker=Ticker("RELIANCE.NSE"))

        op1 = AgentOpinion(
            agent_type=AgentType.FUNDAMENTAL,
            recommendation=RecommendationType.BUY,
            reasoning="Strong refining margins.",
            confidence=ConfidenceScore(Decimal("0.85")),
        )
        op2 = AgentOpinion(
            agent_type=AgentType.QUANT,
            recommendation=RecommendationType.BUY,
            reasoning="Positive momentum factor rank.",
            confidence=ConfidenceScore(Decimal("0.82")),
        )
        report.finalize_consensus([op1, op2])

        is_approved, violations = policy.validate_report_for_approval(report)
        self.assertTrue(is_approved)


if __name__ == "__main__":
    unittest.main()
