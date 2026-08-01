"""
Unit tests for Market Domain Enums.
"""

import unittest

from packages.domain.enums.market import (
    ExchangeType,
    MarketSegment,
    MarketSession,
    MarketStatus,
    SettlementStatus,
    SettlementType,
    Timeframe,
)


class TestMarketEnums(unittest.TestCase):
    """Test suite for Market Enums."""

    def test_exchange_type_members_and_uniqueness(self):
        self.assertEqual(len(ExchangeType), len(set(ExchangeType)))
        self.assertIn("NSE", ExchangeType.__members__)
        self.assertIn("BSE", ExchangeType.__members__)
        self.assertIn("MCX", ExchangeType.__members__)

    def test_exchange_type_helpers(self):
        self.assertTrue(ExchangeType.NSE.is_indian_exchange())
        self.assertTrue(ExchangeType.BSE.is_indian_exchange())
        self.assertTrue(ExchangeType.MCX.is_indian_exchange())
        self.assertFalse(ExchangeType.NYSE.is_indian_exchange())

        self.assertTrue(ExchangeType.NSE.is_equities_exchange())
        self.assertFalse(ExchangeType.MCX.is_equities_exchange())

    def test_exchange_type_string_serialization(self):
        self.assertEqual(str(ExchangeType.NSE), "NSE")
        self.assertEqual(ExchangeType.NSE.value, "NSE")

    def test_market_segment_helpers(self):
        self.assertTrue(MarketSegment.LARGE_CAP.is_equity_cap_segment())
        self.assertFalse(MarketSegment.DERIVATIVES.is_equity_cap_segment())

    def test_market_status_helpers(self):
        self.assertTrue(MarketStatus.OPEN.is_active())
        self.assertFalse(MarketStatus.CLOSED.is_active())
        self.assertTrue(MarketStatus.HALTED.is_halted())
        self.assertTrue(MarketStatus.CIRCUIT_BREAKER_HALT.is_halted())

    def test_settlement_type_helpers(self):
        self.assertEqual(SettlementType.T_PLUS_1.settlement_days(), 1)
        self.assertEqual(SettlementType.T_PLUS_0.settlement_days(), 0)
        self.assertEqual(SettlementType.T_PLUS_2.settlement_days(), 2)

    def test_settlement_status_helpers(self):
        self.assertTrue(SettlementStatus.SETTLED.is_terminal())
        self.assertFalse(SettlementStatus.PENDING.is_terminal())

    def test_market_session_helpers(self):
        self.assertTrue(MarketSession.NORMAL.is_regular_hours())
        self.assertFalse(MarketSession.PRE_MARKET.is_regular_hours())

    def test_timeframe_helpers(self):
        self.assertTrue(Timeframe.MINUTE_1.is_intraday())
        self.assertFalse(Timeframe.DAY_1.is_intraday())
        self.assertFalse(Timeframe.WEEK_1.is_intraday())


if __name__ == "__main__":
    unittest.main()
