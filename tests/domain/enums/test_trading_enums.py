"""
Unit tests for Trading Domain Enums.
"""

import unittest

from packages.domain.enums.trading import (
    AssetType,
    ExecutionStatus,
    OrderStatus,
    OrderType,
    PositionType,
    TradeType,
)


class TestTradingEnums(unittest.TestCase):
    """Test suite for Trading Enums."""

    def test_asset_type_helpers(self):
        self.assertTrue(AssetType.FUTURES.is_derivative())
        self.assertTrue(AssetType.OPTIONS.is_derivative())
        self.assertFalse(AssetType.EQUITY.is_derivative())
        self.assertTrue(AssetType.EQUITY.is_equity_like())
        self.assertTrue(AssetType.REIT.is_equity_like())

    def test_order_type_helpers(self):
        self.assertTrue(OrderType.LIMIT.requires_price())
        self.assertFalse(OrderType.MARKET.requires_price())
        self.assertTrue(OrderType.BRACKET.is_advanced())
        self.assertTrue(OrderType.AMO.is_advanced())

    def test_order_status_helpers(self):
        self.assertTrue(OrderStatus.SUBMITTED.is_active())
        self.assertTrue(OrderStatus.PARTIALLY_FILLED.is_active())
        self.assertFalse(OrderStatus.FILLED.is_active())
        self.assertTrue(OrderStatus.FILLED.is_terminal())
        self.assertTrue(OrderStatus.FILLED.is_filled())

    def test_trade_type_helpers(self):
        self.assertEqual(TradeType.BUY.opposite(), TradeType.SELL)
        self.assertEqual(TradeType.SELL.opposite(), TradeType.BUY)
        self.assertTrue(TradeType.BUY.is_buy())
        self.assertTrue(TradeType.SELL.is_sell())

    def test_position_type_helpers(self):
        self.assertEqual(PositionType.LONG.opposite(), PositionType.SHORT)
        self.assertEqual(PositionType.LONG.quantity_multiplier(), 1)
        self.assertEqual(PositionType.SHORT.quantity_multiplier(), -1)

    def test_execution_status_helpers(self):
        self.assertTrue(ExecutionStatus.EXECUTED.is_successful())
        self.assertTrue(ExecutionStatus.PARTIALLY_EXECUTED.is_successful())
        self.assertFalse(ExecutionStatus.FAILED.is_successful())
        self.assertTrue(ExecutionStatus.FAILED.is_terminal())


if __name__ == "__main__":
    unittest.main()
