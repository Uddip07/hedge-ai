"""
Market Domain Package for the Indian AI Hedge Fund Platform.

Consolidates Company, Asset, Listing, TradingCalendar, TradingSession, MarketHoliday,
SettlementCycle, OHLCV, Candle, and MarketTimestamp.
"""

from packages.domain.market.asset import Asset
from packages.domain.market.calendar import (
    MarketHoliday,
    TradingCalendar,
    TradingSession,
)
from packages.domain.market.company import Company
from packages.domain.market.listing import Listing
from packages.domain.market.market_timestamp import MarketTimestamp
from packages.domain.market.ohlcv import OHLCV, Candle
from packages.domain.market.provider import MarketProvider
from packages.domain.market.quote import MarketQuote
from packages.domain.market.settlement import SettlementCycle

__all__ = [
    "Company",
    "Asset",
    "Listing",
    "TradingCalendar",
    "TradingSession",
    "MarketHoliday",
    "SettlementCycle",
    "OHLCV",
    "Candle",
    "MarketTimestamp",
    "MarketQuote",
    "MarketProvider",
]
