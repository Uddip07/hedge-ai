"""
Market Enums for the Indian AI Hedge Fund Domain.

Defines canonical market abstractions including exchanges, market segments,
statuses, settlement protocols, session states, and granularity timeframes.
"""

from enum import StrEnum


class ExchangeType(StrEnum):
    """
    Financial Exchanges supported by the platform.
    Primary focus is Indian exchanges (NSE, BSE, MCX), with extensibility for global venues.
    """

    NSE = "NSE"
    BSE = "BSE"
    MCX = "MCX"
    NSDL = "NSDL"
    CDSL = "CDSL"
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    AMEX = "AMEX"
    LSE = "LSE"
    TSX = "TSX"
    CRYPTO_GLOBAL = "CRYPTO_GLOBAL"

    def is_indian_exchange(self) -> bool:
        """Return True if the exchange is an Indian financial market venue."""
        return self in {
            ExchangeType.NSE,
            ExchangeType.BSE,
            ExchangeType.MCX,
            ExchangeType.NSDL,
            ExchangeType.CDSL,
        }

    def is_equities_exchange(self) -> bool:
        """Return True if the exchange primarily trades stock equities."""
        return self in {
            ExchangeType.NSE,
            ExchangeType.BSE,
            ExchangeType.NYSE,
            ExchangeType.NASDAQ,
            ExchangeType.AMEX,
            ExchangeType.LSE,
            ExchangeType.TSX,
        }


class MarketSegment(StrEnum):
    """
    Market capitalization and asset classification segments.
    """

    LARGE_CAP = "LARGE_CAP"
    MID_CAP = "MID_CAP"
    SMALL_CAP = "SMALL_CAP"
    MICRO_CAP = "MICRO_CAP"
    CASH = "CASH"
    DERIVATIVES = "DERIVATIVES"
    COMMODITY = "COMMODITY"
    CURRENCY = "CURRENCY"

    def is_equity_cap_segment(self) -> bool:
        """Return True if this segment is based on company market capitalization."""
        return self in {
            MarketSegment.LARGE_CAP,
            MarketSegment.MID_CAP,
            MarketSegment.SMALL_CAP,
            MarketSegment.MICRO_CAP,
        }


class MarketStatus(StrEnum):
    """
    Trading market operational status states.
    """

    PRE_OPEN = "PRE_OPEN"
    OPEN = "OPEN"
    POST_CLOSE = "POST_CLOSE"
    CLOSED = "CLOSED"
    HALTED = "HALTED"
    CIRCUIT_BREAKER_HALT = "CIRCUIT_BREAKER_HALT"

    def is_active(self) -> bool:
        """Return True if orders can actively execute in this market state."""
        return self == MarketStatus.OPEN

    def is_halted(self) -> bool:
        """Return True if trading is temporarily suspended."""
        return self in {MarketStatus.HALTED, MarketStatus.CIRCUIT_BREAKER_HALT}


class SettlementType(StrEnum):
    """
    Trade settlement cycle protocols (e.g. Indian market T+1 equity settlement).
    """

    T_PLUS_0 = "T+0"
    T_PLUS_1 = "T+1"
    T_PLUS_2 = "T+2"
    T_PLUS_3 = "T+3"
    SAME_DAY = "SAME_DAY"

    def settlement_days(self) -> int:
        """Return the number of business days required for trade settlement."""
        days_map = {
            SettlementType.T_PLUS_0: 0,
            SettlementType.SAME_DAY: 0,
            SettlementType.T_PLUS_1: 1,
            SettlementType.T_PLUS_2: 2,
            SettlementType.T_PLUS_3: 3,
        }
        return days_map[self]


class SettlementStatus(StrEnum):
    """
    Status of security and cash settlement lifecycle.
    """

    PENDING = "PENDING"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    PARTIALLY_SETTLED = "PARTIALLY_SETTLED"
    CANCELLED = "CANCELLED"

    def is_terminal(self) -> bool:
        """Return True if settlement has reached a final state."""
        return self in {
            SettlementStatus.SETTLED,
            SettlementStatus.FAILED,
            SettlementStatus.CANCELLED,
        }


class MarketSession(StrEnum):
    """
    Trading session intervals throughout a market day.
    """

    PRE_MARKET = "PRE_MARKET"
    NORMAL = "NORMAL"
    POST_MARKET = "POST_MARKET"
    SPECIAL = "SPECIAL"
    BLOCK_DEAL = "BLOCK_DEAL"

    def is_regular_hours(self) -> bool:
        """Return True if this is the standard continuous trading session."""
        return self == MarketSession.NORMAL


class Timeframe(StrEnum):
    """
    OHLCV bar aggregation timeframes.
    """

    TICK = "TICK"
    SECOND_1 = "1S"
    SECOND_5 = "5S"
    MINUTE_1 = "1M"
    MINUTE_3 = "3M"
    MINUTE_5 = "5M"
    MINUTE_15 = "15M"
    MINUTE_30 = "30M"
    HOUR_1 = "1H"
    HOUR_4 = "4H"
    DAY_1 = "1D"
    WEEK_1 = "1W"
    MONTH_1 = "1MN"

    def is_intraday(self) -> bool:
        """Return True if the timeframe is shorter than or equal to 1 day."""
        return self in {
            Timeframe.TICK,
            Timeframe.SECOND_1,
            Timeframe.SECOND_5,
            Timeframe.MINUTE_1,
            Timeframe.MINUTE_3,
            Timeframe.MINUTE_5,
            Timeframe.MINUTE_15,
            Timeframe.MINUTE_30,
            Timeframe.HOUR_1,
            Timeframe.HOUR_4,
        }
