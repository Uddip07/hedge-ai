"""
Unit tests for Strategy Domain Enums.
"""

import unittest

from packages.domain.enums.strategy import (
    PaperTradeStatus,
    SignalStrength,
    SignalType,
    StrategyType,
)


class TestStrategyEnums(unittest.TestCase):
    """Test suite for Strategy Enums."""

    def test_strategy_type_helpers(self):
        self.assertTrue(StrategyType.MOMENTUM.is_quantitative_factor())
        self.assertTrue(StrategyType.MULTI_FACTOR.is_quantitative_factor())
        self.assertTrue(StrategyType.STAT_ARB.is_statistical_arbitrage())
        self.assertTrue(StrategyType.PAIRS.is_statistical_arbitrage())

    def test_signal_type_helpers(self):
        self.assertTrue(SignalType.BUY.is_entry())
        self.assertTrue(SignalType.SELL.is_entry())
        self.assertFalse(SignalType.HOLD.is_entry())
        self.assertTrue(SignalType.EXIT_LONG.is_exit())

    def test_signal_strength_helpers(self):
        self.assertEqual(SignalStrength.VERY_STRONG.score_multiplier(), 1.0)
        self.assertEqual(SignalStrength.WEAK.score_multiplier(), 0.25)

    def test_paper_trade_status_helpers(self):
        self.assertTrue(PaperTradeStatus.ACTIVE.is_open())
        self.assertTrue(PaperTradeStatus.CLOSED.is_terminal())


if __name__ == "__main__":
    unittest.main()
