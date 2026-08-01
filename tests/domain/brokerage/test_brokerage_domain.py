"""
Unit tests for BrokerAccount Aggregate Root and child brokerage models (Order, Execution, AccountBalance, MarginRequirement).
"""

import unittest
from decimal import Decimal

from packages.domain.brokerage import (
    AccountBalance,
    BrokerAccount,
    Execution,
    MarginRequirement,
    Order,
)
from packages.domain.enums.system import BrokerType
from packages.domain.enums.trading import OrderStatus, OrderType, TradeType
from packages.domain.exceptions import InsufficientFundsError, OrderValidationError
from packages.domain.value_objects.core import Money, Price, Quantity
from packages.domain.value_objects.identifiers import BrokerId, OrderId, PortfolioId, Ticker
from packages.domain.value_objects.temporal import Timestamp


class TestBrokerageDomain(unittest.TestCase):
    """Test suite for BrokerAccount Aggregate Root and brokerage models."""

    def test_account_balance_and_margin(self):
        bal = AccountBalance(
            available_cash=Money(Decimal("100000.00")),
            used_margin=Money(Decimal("10000.00")),
            unrealized_pnl=Money(Decimal("2000.00")),
        )
        self.assertEqual(bal.total_buying_power.amount, Decimal("92000.00"))

        margin = MarginRequirement(
            initial_margin=Money(Decimal("20000.00")),
            maintenance_margin=Money(Decimal("15000.00")),
        )
        self.assertTrue(margin.is_margin_call(Money(Decimal("14000.00"))))
        self.assertFalse(margin.is_margin_call(Money(Decimal("16000.00"))))

    def test_execution_net_amounts(self):
        t = Ticker("RELIANCE.NSE")
        ex_buy = Execution(
            order_id=OrderId.generate(),
            ticker=t,
            trade_type=TradeType.BUY,
            quantity=Quantity(Decimal("10")),
            price=Price.from_amount("2500"),
            fee=Money(Decimal("20.00")),
            tax=Money(Decimal("10.00")),
            executed_at=Timestamp.now_utc(),
        )

        self.assertEqual(ex_buy.gross_amount.amount, Decimal("25000.00"))
        self.assertEqual(ex_buy.net_amount.amount, Decimal("25030.00"))

    def test_order_lifecycle_and_filling(self):
        t = Ticker("INFY.NSE")
        p_id = PortfolioId.generate()
        b_id = BrokerId.generate()

        # Limit order requires price
        with self.assertRaises(OrderValidationError):
            Order(
                portfolio_id=p_id,
                broker_account_id=b_id,
                ticker=t,
                order_type=OrderType.LIMIT,
                trade_type=TradeType.BUY,
                quantity=Quantity(Decimal("10")),
            )

        order = Order(
            portfolio_id=p_id,
            broker_account_id=b_id,
            ticker=t,
            order_type=OrderType.LIMIT,
            trade_type=TradeType.BUY,
            quantity=Quantity(Decimal("10")),
            price=Price.from_amount("1500"),
        )
        self.assertTrue(order.is_active)
        self.assertEqual(order.remaining_quantity.value, Decimal("10"))

        # Partial fill (5 shares)
        ex1 = order.fill(Quantity(Decimal("5")), Price.from_amount("1500"))
        self.assertEqual(order.status, OrderStatus.PARTIALLY_FILLED)
        self.assertEqual(order.remaining_quantity.value, Decimal("5"))

        # Complete fill (remaining 5 shares)
        ex2 = order.fill(Quantity(Decimal("5")), Price.from_amount("1500"))
        self.assertEqual(order.status, OrderStatus.FILLED)
        self.assertTrue(order.is_filled)
        self.assertFalse(order.is_active)

    def test_broker_account_aggregate_workflow(self):
        b_id = BrokerId.generate()
        acc = BrokerAccount(
            id=b_id,
            account_number="DHAN-100234",
            broker_type=BrokerType.DHAN,
            balance=AccountBalance(available_cash=Money(Decimal("50000.00"))),
        )

        t = Ticker("RELIANCE.NSE")
        order = Order(
            portfolio_id=PortfolioId.generate(),
            broker_account_id=b_id,
            ticker=t,
            order_type=OrderType.LIMIT,
            trade_type=TradeType.BUY,
            quantity=Quantity(Decimal("10")),
            price=Price.from_amount("2500"),
        )

        # Place order
        acc.place_order(order)
        self.assertIn(str(order.id), acc.orders)

        # Execute fill for 10 shares @ 2500 (fee 50) -> net cost 25050
        execution = acc.execute_order_fill(
            order_id=order.id,
            fill_quantity=Quantity(Decimal("10")),
            fill_price=Price.from_amount("2500"),
            fee=Money(Decimal("50.00")),
        )

        self.assertEqual(len(acc.executions), 1)
        # Cash balance debited: 50000 - 25050 = 24950
        self.assertEqual(acc.balance.available_cash.amount, Decimal("24950.00"))

        # Excessive order placement rejected
        excessive_order = Order(
            portfolio_id=PortfolioId.generate(),
            broker_account_id=b_id,
            ticker=t,
            order_type=OrderType.LIMIT,
            trade_type=TradeType.BUY,
            quantity=Quantity(Decimal("100")),
            price=Price.from_amount("2500"),  # total 250,000 exceeds 24,950
        )
        with self.assertRaises(InsufficientFundsError):
            acc.place_order(excessive_order)


if __name__ == "__main__":
    unittest.main()
