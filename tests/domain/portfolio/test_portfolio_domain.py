"""
Unit tests for Portfolio Aggregate Root and child domain entities (Holding, Position, Trade, Snapshots, RebalancePlan).
"""

import unittest
from decimal import Decimal

from packages.domain.enums.portfolio import AllocationMethod, PortfolioType
from packages.domain.enums.trading import PositionType, TradeType
from packages.domain.exceptions import InsufficientFundsError
from packages.domain.portfolio import (
    Allocation,
    Holding,
    Portfolio,
    Position,
    RebalancePlan,
    Trade,
)
from packages.domain.value_objects.core import Money, Price, Quantity, Weight
from packages.domain.value_objects.identifiers import OrderId, PortfolioId, Ticker
from packages.domain.value_objects.temporal import Timestamp


class TestPortfolioDomain(unittest.TestCase):
    """Test suite for Portfolio Aggregate Root and portfolio models."""

    def test_holding_calculations_and_add_shares(self):
        t = Ticker("RELIANCE.NSE")
        holding = Holding(
            ticker=t,
            quantity=Quantity(Decimal("10")),
            average_buy_price=Price.from_amount("2500"),
            current_price=Price.from_amount("2700"),
        )

        self.assertEqual(holding.invested_value.amount, Decimal("25000.00"))
        self.assertEqual(holding.current_value.amount, Decimal("27000.00"))
        self.assertEqual(holding.unrealized_pnl.amount, Decimal("2000.00"))
        self.assertEqual(holding.unrealized_pnl_pct.value, Decimal("8.00"))

        # Add 10 more shares at 2900 -> avg buy price becomes 2700
        holding.add_shares(Quantity(Decimal("10")), Price.from_amount("2900"))
        self.assertEqual(holding.quantity.value, Decimal("20"))
        self.assertEqual(holding.average_buy_price.amount, Decimal("2700.00"))

    def test_position_lifecycle_and_realized_pnl(self):
        t = Ticker("INFY.NSE")
        ts_open = Timestamp.now_utc()
        pos = Position(
            ticker=t,
            position_type=PositionType.LONG,
            quantity=Quantity(Decimal("50")),
            entry_price=Price.from_amount("1400"),
            opened_at=ts_open,
        )

        self.assertTrue(pos.is_open)
        self.assertFalse(pos.is_closed)

        # Close position at 1500 -> realized PnL = (1500 - 1400) * 50 = +5000
        ts_close = Timestamp.now_utc()
        realized = pos.close_position(Price.from_amount("1500"), ts_close)

        self.assertTrue(pos.is_closed)
        self.assertEqual(realized.amount, Decimal("5000.00"))
        assert pos.realized_pnl_money is not None
        self.assertEqual(pos.realized_pnl_money.amount, Decimal("5000.00"))

    def test_trade_net_amount_calculations(self):
        t = Ticker("TCS.NSE")
        ts = Timestamp.now_utc()
        p_id = PortfolioId.generate()
        trade_buy = Trade(
            portfolio_id=p_id,
            order_id=OrderId.generate(),
            ticker=t,
            trade_type=TradeType.BUY,
            quantity=Quantity(Decimal("10")),
            price=Price.from_amount("3000"),
            fee=Money(Decimal("20.00")),
            tax=Money(Decimal("15.00")),
            executed_at=ts,
        )

        self.assertEqual(trade_buy.gross_amount.amount, Decimal("30000.00"))
        # Buy Net Amount = Gross + Fee + Tax = 30000 + 20 + 15 = 30035
        self.assertEqual(trade_buy.net_amount.amount, Decimal("30035.00"))

        trade_sell = Trade(
            portfolio_id=p_id,
            order_id=OrderId.generate(),
            ticker=t,
            trade_type=TradeType.SELL,
            quantity=Quantity(Decimal("10")),
            price=Price.from_amount("3200"),
            fee=Money(Decimal("20.00")),
            tax=Money(Decimal("15.00")),
            executed_at=ts,
        )
        self.assertEqual(trade_sell.gross_amount.amount, Decimal("32000.00"))
        # Sell Net Amount = Gross - Fee - Tax = 32000 - 20 - 15 = 31965
        self.assertEqual(trade_sell.net_amount.amount, Decimal("31965.00"))

    def test_rebalance_plan_validations(self):
        t1 = Ticker("RELIANCE.NSE")
        t2 = Ticker("INFY.NSE")
        plan = RebalancePlan(
            portfolio_id=PortfolioId.generate(),
            method=AllocationMethod.EQUAL_WEIGHT,
            allocations=[
                Allocation(ticker=t1, weight=Weight(Decimal("0.50"))),
                Allocation(ticker=t2, weight=Weight(Decimal("0.50"))),
            ],
        )

        self.assertEqual(plan.total_weight_ratio(), Decimal("1.00"))
        self.assertTrue(plan.is_valid())

    def test_portfolio_aggregate_root_workflow(self):
        port = Portfolio(name="Indian Growth Alpha Portfolio", portfolio_type=PortfolioType.PAPER)
        self.assertEqual(port.cash_balance.amount, Decimal("0.00"))

        # Deposit 100,000 INR
        port.deposit_cash(Money(Decimal("100000.00")))
        self.assertEqual(port.cash_balance.amount, Decimal("100000.00"))

        # Record BUY trade for RELIANCE (10 shares @ 2500, fee 50) -> net 25050
        t_rel = Ticker("RELIANCE.NSE")
        ts = Timestamp.now_utc()
        trade_buy = Trade(
            portfolio_id=port.id,
            order_id=OrderId.generate(),
            ticker=t_rel,
            trade_type=TradeType.BUY,
            quantity=Quantity(Decimal("10")),
            price=Price.from_amount("2500"),
            fee=Money(Decimal("50.00")),
            executed_at=ts,
        )

        port.record_trade(trade_buy)
        self.assertEqual(port.cash_balance.amount, Decimal("74950.00"))
        self.assertIn(t_rel.full_symbol, port.holdings)
        self.assertEqual(len(port.positions), 1)

        # Update market price & check total equity
        port.update_holding_price(t_rel, Price.from_amount("2700"))
        # Holdings value = 10 * 2700 = 27000. Cash = 74950. Total Equity = 101950
        self.assertEqual(port.total_equity().amount, Decimal("101950.00"))

        # Create snapshot
        snap = port.create_snapshot()
        self.assertEqual(snap.total_equity.amount, Decimal("101950.00"))
        self.assertEqual(len(port.snapshots), 1)

        # Record SELL trade for RELIANCE (10 shares @ 2700, fee 50) -> net 26950
        trade_sell = Trade(
            portfolio_id=port.id,
            order_id=OrderId.generate(),
            ticker=t_rel,
            trade_type=TradeType.SELL,
            quantity=Quantity(Decimal("10")),
            price=Price.from_amount("2700"),
            fee=Money(Decimal("50.00")),
            executed_at=ts,
        )
        port.record_trade(trade_sell)

        # Cash balance = 74950 + 26950 = 101900. Holding removed.
        self.assertEqual(port.cash_balance.amount, Decimal("101900.00"))
        self.assertNotIn(t_rel.full_symbol, port.holdings)

        # Insufficient funds error check
        with self.assertRaises(InsufficientFundsError):
            port.withdraw_cash(Money(Decimal("200000.00")))


if __name__ == "__main__":
    unittest.main()
