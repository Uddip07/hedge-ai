"""
Quote & OHLCV Response Mapper.

Maps raw validated quote & candle data into domain entities and value objects.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from packages.domain.enums.market import Timeframe
from packages.domain.market.ohlcv import OHLCV, Candle
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.core.quantity import Quantity
from packages.domain.value_objects.identifiers.currency import Currency
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp
from packages.infrastructure.market_data.models import MarketQuote


class QuoteMapper:
    """Mapper for real-time price quotes and OHLCV candles."""

    @staticmethod
    def _parse_ts(ts_val: Any) -> Timestamp:
        if ts_val is None:
            return Timestamp.now_utc()
        if isinstance(ts_val, Timestamp):
            return ts_val
        if isinstance(ts_val, datetime):
            return Timestamp(value=ts_val)
        if isinstance(ts_val, str):
            return Timestamp.from_iso(ts_val)
        return Timestamp.now_utc()

    @classmethod
    def to_market_quote(cls, ticker: Ticker, raw: dict[str, Any]) -> MarketQuote:
        p_val = Decimal(str(raw.get("last_price", raw.get("close", raw.get("price", "1000.00")))))
        chg = Decimal(str(raw.get("change_percent", raw.get("change_24h", "0.00"))))
        vol = Decimal(str(raw.get("volume", raw.get("volume_24h", "0.00"))))
        ts = cls._parse_ts(raw.get("timestamp"))

        price_obj = Price(money=Money(amount=p_val, currency=Currency()))

        return MarketQuote(
            ticker=ticker,
            price=price_obj,
            change_24h=chg,
            volume_24h=vol,
            timestamp=ts,
        )

    @classmethod
    def to_candles(
        cls, ticker: Ticker, timeframe: Timeframe, raw_list: list[dict[str, Any]]
    ) -> list[Candle]:
        candles: list[Candle] = []
        for item in raw_list:
            o_p = Decimal(str(item.get("open", "1000.00")))
            h_p = Decimal(str(item.get("high", "1010.00")))
            l_p = Decimal(str(item.get("low", "990.00")))
            c_p = Decimal(str(item.get("close", "1005.00")))
            vol = Decimal(str(item.get("volume", 1000)))
            ts = cls._parse_ts(item.get("date", item.get("timestamp")))

            ohlcv = OHLCV(
                open=Price(money=Money(amount=o_p, currency=Currency())),
                high=Price(money=Money(amount=h_p, currency=Currency())),
                low=Price(money=Money(amount=l_p, currency=Currency())),
                close=Price(money=Money(amount=c_p, currency=Currency())),
                volume=Quantity(vol),
            )
            candle = Candle(timestamp=ts, timeframe=timeframe, ohlcv=ohlcv)
            candles.append(candle)
        return candles
