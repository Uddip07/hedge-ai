"""
MarketQuote Domain Model for the Indian AI Hedge Fund Platform.

Represents a normalized market price quote snapshot with pricing metrics, 24h changes,
volume, session high/low, previous close, exchange status, and timestamp.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from packages.domain.enums.market import ExchangeType, MarketStatus
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True)
class MarketQuote:
    """
    Normalized Market Quote Domain Model.

    Attributes:
        ticker (Ticker): Target asset ticker identifier.
        exchange (ExchangeType): Venue exchange (NSE, BSE, etc.).
        price (Price): Current market price.
        change (Decimal): Absolute price change vs previous close.
        change_percent (Decimal): Percentage price change vs previous close (e.g. 1.25 for +1.25%).
        volume (Decimal): Trading volume.
        open (Decimal): Session open price.
        high (Decimal): Session high price.
        low (Decimal): Session low price.
        previous_close (Decimal): Previous trading session close price.
        currency (str): Price currency code (e.g. "INR").
        timestamp (Timestamp): Quote timestamp in UTC.
        market_status (MarketStatus): Real-time exchange status (OPEN, CLOSED, PRE_OPEN, POST_CLOSE).
    """

    ticker: Ticker
    exchange: ExchangeType
    price: Price
    change: Decimal = Decimal("0.00")
    change_percent: Decimal = Decimal("0.00")
    volume: Decimal = Decimal("0.00")
    open: Decimal = Decimal("0.00")
    high: Decimal = Decimal("0.00")
    low: Decimal = Decimal("0.00")
    previous_close: Decimal = Decimal("0.00")
    currency: str = "INR"
    timestamp: Timestamp = field(default_factory=Timestamp.now_utc)
    market_status: MarketStatus = MarketStatus.OPEN

    def to_dict(self) -> dict[str, Any]:
        """Serialize MarketQuote to dictionary."""
        return {
            "ticker": self.ticker.full_symbol,
            "symbol": self.ticker.symbol,
            "exchange": self.exchange.value,
            "price": str(self.price.amount),
            "change": str(self.change),
            "change_percent": str(self.change_percent),
            "volume": str(self.volume),
            "open": str(self.open),
            "high": str(self.high),
            "low": str(self.low),
            "previous_close": str(self.previous_close),
            "currency": self.currency,
            "timestamp": self.timestamp.isoformat(),
            "market_status": self.market_status.value,
            "is_market_open": self.market_status == MarketStatus.OPEN,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MarketQuote":
        """Deserialize dictionary to MarketQuote."""
        from packages.domain.enums.system import CurrencyCode
        from packages.domain.value_objects.core.money import Money
        from packages.domain.value_objects.identifiers.currency import Currency

        ticker = (
            Ticker.from_dict(data["ticker"])
            if isinstance(data["ticker"], dict)
            else Ticker(data["ticker"])
        )
        exch = ExchangeType(data.get("exchange", "NSE"))
        curr_str = data.get("currency", "INR")
        curr = Currency(CurrencyCode(curr_str))
        price_val = Decimal(str(data["price"]))

        status_val = data.get("market_status", "OPEN")
        market_status = MarketStatus(status_val) if isinstance(status_val, str) else status_val

        return cls(
            ticker=ticker,
            exchange=exch,
            price=Price(money=Money(amount=price_val, currency=curr)),
            change=Decimal(str(data.get("change", "0.00"))),
            change_percent=Decimal(str(data.get("change_percent", "0.00"))),
            volume=Decimal(str(data.get("volume", "0.00"))),
            open=Decimal(str(data.get("open", "0.00"))),
            high=Decimal(str(data.get("high", "0.00"))),
            low=Decimal(str(data.get("low", "0.00"))),
            previous_close=Decimal(str(data.get("previous_close", "0.00"))),
            currency=curr_str,
            timestamp=(
                Timestamp.from_iso(data["timestamp"])
                if "timestamp" in data
                else Timestamp.now_utc()
            ),
            market_status=market_status,
        )
