"""
Unit tests for Temporal Value Objects (Timestamp, MarketTimestamp, TradingDate, FiscalYear, ReportingPeriod, PriceRange).
"""

import unittest
from datetime import UTC, date, datetime
from decimal import Decimal

from packages.domain.enums.market import MarketSession
from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.temporal import (
    FiscalYear,
    MarketTimestamp,
    PriceRange,
    ReportingPeriod,
    Timestamp,
    TradingDate,
)


class TestTemporalValueObjects(unittest.TestCase):
    """Test suite for temporal value objects."""

    def test_timestamp_timezone_awareness_and_parsing(self):
        ts_now = Timestamp.now_utc()
        self.assertIsNotNone(ts_now.value.tzinfo)

        # Naive datetime should automatically be assigned UTC
        naive_dt = datetime(2026, 7, 23, 10, 0, 0)
        ts_naive = Timestamp(naive_dt)
        self.assertEqual(ts_naive.value.tzinfo, UTC)

        # ISO parsing
        ts_parsed = Timestamp.from_iso("2026-07-23T10:00:00+05:30")
        self.assertEqual(ts_parsed.date, date(2026, 7, 23))

    def test_market_timestamp(self):
        ts = Timestamp.now_utc()
        mts = MarketTimestamp(timestamp=ts, session=MarketSession.NORMAL)
        self.assertTrue(mts.is_regular_hours())

        mts_dict = mts.to_dict()
        restored = MarketTimestamp.from_dict(mts_dict)
        self.assertEqual(mts.session, restored.session)

    def test_trading_date(self):
        td_sat = TradingDate(date(2026, 7, 25))  # Saturday
        self.assertTrue(td_sat.is_weekend())

        td_mon = TradingDate.from_dict("2026-07-27")  # Monday
        self.assertFalse(td_mon.is_weekend())

    def test_fiscal_year_indian_cycle(self):
        fy = FiscalYear(start_year=2025)
        self.assertEqual(fy.end_year, 2026)
        self.assertEqual(fy.label, "FY2025-26")
        self.assertEqual(fy.start_date, date(2025, 4, 1))
        self.assertEqual(fy.end_date, date(2026, 3, 31))

    def test_reporting_period_annual_and_quarterly(self):
        fy = FiscalYear(start_year=2025)

        rp_q1 = ReportingPeriod(fiscal_year=fy, quarter=1)
        self.assertTrue(rp_q1.is_quarterly())
        self.assertFalse(rp_q1.is_annual())
        self.assertEqual(rp_q1.label, "Q1 FY2025-26")

        rp_annual = ReportingPeriod(fiscal_year=fy, quarter=None)
        self.assertTrue(rp_annual.is_annual())
        self.assertEqual(rp_annual.label, "FY2025-26 Annual")

        with self.assertRaises(ValidationError):
            ReportingPeriod(fiscal_year=fy, quarter=5)  # Invalid quarter

    def test_price_range_validation_and_spread(self):
        p_low = Price.from_amount("100.00")
        p_high = Price.from_amount("120.00")
        p_open = Price.from_amount("105.00")
        p_close = Price.from_amount("115.00")

        pr = PriceRange(low=p_low, high=p_high, open=p_open, close=p_close)
        self.assertEqual(pr.spread_money.amount, Decimal("20.00"))
        self.assertTrue(pr.contains(Price.from_amount("110.00")))
        self.assertFalse(pr.contains(Price.from_amount("125.00")))

        # Inverted bounds error
        with self.assertRaises(ValidationError):
            PriceRange(low=p_high, high=p_low)

        # Open outside low/high bounds error
        with self.assertRaises(ValidationError):
            PriceRange(low=p_low, high=p_high, open=Price.from_amount("130.00"))


if __name__ == "__main__":
    unittest.main()
