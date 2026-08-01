"""
Unit tests for Market Domain Entities and Models (Company, Asset, Listing, TradingCalendar, SettlementCycle, OHLCV, Candle).
"""

import unittest
import uuid
from datetime import date
from decimal import Decimal

from packages.domain.enums.market import (
    ExchangeType,
    MarketSegment,
    SettlementType,
    Timeframe,
)
from packages.domain.enums.trading import AssetType
from packages.domain.exceptions import DuplicateEntityError, EntityNotFoundError, ValidationError
from packages.domain.market import (
    OHLCV,
    Asset,
    Candle,
    Company,
    Listing,
    MarketHoliday,
    SettlementCycle,
    TradingCalendar,
)
from packages.domain.value_objects.core import Price, Quantity
from packages.domain.value_objects.identifiers import ISIN, Ticker
from packages.domain.value_objects.temporal import Timestamp, TradingDate


class TestMarketDomain(unittest.TestCase):
    """Test suite for Market Domain entities and models."""

    def test_company_and_listing_management(self):
        comp = Company(
            name="Reliance Industries Limited", sector=MarketSegment.LARGE_CAP, industry="Oil & Gas"
        )
        self.assertEqual(comp.name, "Reliance Industries Limited")
        self.assertEqual(len(comp.listings), 0)

        t_nse = Ticker("RELIANCE.NSE")
        isin = ISIN("INE002A01018")
        listing_nse = Listing(
            company_id=comp.id, exchange=ExchangeType.NSE, ticker=t_nse, isin=isin
        )

        comp.add_listing(listing_nse)
        self.assertEqual(len(comp.listings), 1)
        self.assertEqual(comp.get_primary_listing(), listing_nse)

        # Duplicate listing for same exchange rejected
        with self.assertRaises(DuplicateEntityError):
            comp.add_listing(listing_nse)

        # Remove listing
        comp.remove_listing(listing_nse.id)
        self.assertEqual(len(comp.listings), 0)

        with self.assertRaises(EntityNotFoundError):
            comp.remove_listing(uuid.uuid4())

    def test_asset_entity_and_validations(self):
        t = Ticker("INFY.NSE")
        asset = Asset(
            ticker=t,
            name="Infosys Limited",
            asset_type=AssetType.EQUITY,
            lot_size=1,
            tick_size=Decimal("0.05"),
        )

        self.assertFalse(asset.is_derivative())

        # Validate order quantity
        asset.validate_order_quantity(Quantity(Decimal("10")))

        # Validate order price (aligned to 0.05 tick size)
        asset.validate_order_price(Price.from_amount("1500.05"))

        # Misaligned tick size price error
        with self.assertRaises(ValidationError):
            asset.validate_order_price(Price.from_amount("1500.03"))

    def test_trading_calendar_and_sessions(self):
        cal = TradingCalendar(exchange=ExchangeType.NSE)
        holiday_diwali = MarketHoliday(
            holiday_date=date(2026, 11, 1), description="Diwali", exchange=ExchangeType.NSE
        )
        cal.holidays.append(holiday_diwali)

        # Sunday is not a trading day
        sun = TradingDate(date(2026, 7, 26))
        self.assertFalse(cal.is_trading_day(sun))

        # Holiday is not a trading day
        diwali_date = TradingDate(date(2026, 11, 1))
        self.assertFalse(cal.is_trading_day(diwali_date))

        # Regular weekday is a trading day
        mon = TradingDate(date(2026, 7, 27))
        self.assertTrue(cal.is_trading_day(mon))

    def test_settlement_cycle_t_plus_1(self):
        trade_dt = TradingDate(date(2026, 7, 24))  # Friday
        sc = SettlementCycle(settlement_type=SettlementType.T_PLUS_1, trade_date=trade_dt)

        # T+1 from Friday skips Saturday & Sunday -> settles Monday July 27
        settlement_dt = sc.calculate_settlement_date()
        self.assertEqual(settlement_dt.value, date(2026, 7, 27))

    def test_ohlcv_and_candle(self):
        p_open = Price.from_amount("100.00")
        p_high = Price.from_amount("120.00")
        p_low = Price.from_amount("95.00")
        p_close = Price.from_amount("115.00")
        vol = Quantity(Decimal("5000"))

        ohlcv = OHLCV(open=p_open, high=p_high, low=p_low, close=p_close, volume=vol)
        self.assertTrue(ohlcv.is_bullish())
        self.assertFalse(ohlcv.is_bearish())
        self.assertEqual(ohlcv.body_size_money().amount, Decimal("15.00"))

        ts = Timestamp.now_utc()
        candle = Candle(timestamp=ts, timeframe=Timeframe.DAY_1, ohlcv=ohlcv)
        self.assertEqual(candle.open, p_open)
        self.assertEqual(candle.close, p_close)
        self.assertTrue(candle.is_bullish())

        # Invalid OHLCV range error (high < low)
        with self.assertRaises(ValidationError):
            OHLCV(open=p_open, high=p_low, low=p_high, close=p_close, volume=vol)


if __name__ == "__main__":
    unittest.main()
