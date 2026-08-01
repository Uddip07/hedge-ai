"""
Currency, Exchange, and Financial Statement Normalizers.
"""

from typing import Any

from packages.domain.enums.market import ExchangeType, Timeframe
from packages.domain.enums.system import CurrencyCode
from packages.domain.value_objects.identifiers.currency import Currency


class CurrencyNormalizer:
    """Normalizes currency strings to domain Currency value objects."""

    _CURRENCY_MAP: dict[str, CurrencyCode] = {
        "INR": CurrencyCode.INR,
        "RS": CurrencyCode.INR,
        "RUPEE": CurrencyCode.INR,
        "USD": CurrencyCode.USD,
        "$": CurrencyCode.USD,
        "EUR": CurrencyCode.EUR,
        "GBP": CurrencyCode.GBP,
    }

    @classmethod
    def normalize(cls, raw_currency: Any) -> Currency:
        if isinstance(raw_currency, Currency):
            return raw_currency
        code_str = str(raw_currency).upper().strip()
        code_enum = cls._CURRENCY_MAP.get(code_str, CurrencyCode.INR)
        return Currency(code=code_enum)


class ExchangeNormalizer:
    """Normalizes exchange strings to domain ExchangeType enums."""

    _EXCHANGE_MAP: dict[str, ExchangeType] = {
        "NSE": ExchangeType.NSE,
        "NATIONAL STOCK EXCHANGE": ExchangeType.NSE,
        "BSE": ExchangeType.BSE,
        "BOMBAY STOCK EXCHANGE": ExchangeType.BSE,
        "MCX": ExchangeType.MCX,
        "NYSE": ExchangeType.NYSE,
        "NASDAQ": ExchangeType.NASDAQ,
        "LSE": ExchangeType.LSE,
    }

    @classmethod
    def normalize(cls, raw_exchange: Any) -> ExchangeType:
        if isinstance(raw_exchange, ExchangeType):
            return raw_exchange
        ex_str = str(raw_exchange).upper().strip()
        return cls._EXCHANGE_MAP.get(ex_str, ExchangeType.NSE)


class TimeframeNormalizer:
    """Normalizes timeframe/interval strings to domain Timeframe enums."""

    _TIMEFRAME_MAP: dict[str, Timeframe] = {
        "1D": Timeframe.DAY_1,
        "DAY": Timeframe.DAY_1,
        "DAILY": Timeframe.DAY_1,
        "1H": Timeframe.HOUR_1,
        "HOUR": Timeframe.HOUR_1,
        "15M": Timeframe.MINUTE_15,
        "5M": Timeframe.MINUTE_5,
        "1M": Timeframe.MINUTE_1,
        "1W": Timeframe.WEEK_1,
        "WEEKLY": Timeframe.WEEK_1,
        "MONTHLY": Timeframe.MONTH_1,
    }

    @classmethod
    def normalize(cls, raw_timeframe: Any) -> Timeframe:
        if isinstance(raw_timeframe, Timeframe):
            return raw_timeframe
        tf_str = str(raw_timeframe).upper().strip()
        return cls._TIMEFRAME_MAP.get(tf_str, Timeframe.DAY_1)
