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
        chg = Decimal(str(raw.get("change", "0.00")))
        chg_pct = Decimal(str(raw.get("change_percent", raw.get("change_24h", "0.00"))))
        vol = Decimal(str(raw.get("volume", raw.get("volume_24h", "0.00"))))
        open_p = Decimal(str(raw.get("open", p_val)))
        high_p = Decimal(str(raw.get("high", p_val)))
        low_p = Decimal(str(raw.get("low", p_val)))
        prev_close = Decimal(str(raw.get("previous_close", p_val)))
        ts = cls._parse_ts(raw.get("timestamp"))
        market_status = str(raw.get("market_status", "CLOSED"))
        source = str(raw.get("source", "YAHOO"))
        yahoo_sym = str(raw.get("yahoo_symbol", ""))

        price_obj = Price(money=Money(amount=p_val, currency=Currency()))

        return MarketQuote(
            ticker=ticker,
            price=price_obj,
            change=chg,
            change_percent=chg_pct,
            volume=vol,
            open=open_p,
            high=high_p,
            low=low_p,
            previous_close=prev_close,
            change_24h=chg_pct,
            volume_24h=vol,
            timestamp=ts,
            market_status=market_status,
            source=source,
            yahoo_symbol=yahoo_sym,
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
