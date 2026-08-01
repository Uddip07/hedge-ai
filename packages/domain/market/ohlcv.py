"""
OHLCV and Candle Value Objects for the Indian AI Hedge Fund Domain.

Provides market bar data abstractions (Open, High, Low, Close, Volume) and Candle wrappers.
Immutable, self-validating, zero floating point inaccuracies.
"""

from dataclasses import dataclass
from typing import Any

from packages.domain.enums.market import Timeframe
from packages.domain.exceptions import ValidationError
from packages.domain.utils.math import to_decimal
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.core.quantity import Quantity
from packages.domain.value_objects.temporal.price_range import PriceRange
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, slots=True)
class OHLCV:
    """
    Immutable value object representing an Open-High-Low-Close-Volume price bar.

    Attributes:
        open (Price): Opening price.
        high (Price): Period highest price.
        low (Price): Period lowest price.
        close (Price): Closing price.
        volume (Quantity): Trading volume quantity.
    """

    open: Price
    high: Price
    low: Price
    close: Price
    volume: Quantity

    def __post_init__(self) -> None:
        if (
            not isinstance(self.open, Price)
            or not isinstance(self.high, Price)
            or not isinstance(self.low, Price)
            or not isinstance(self.close, Price)
        ):
            raise ValidationError("OHLCV prices must be valid Price instances.")
        if not isinstance(self.volume, Quantity):
            object.__setattr__(self, "volume", Quantity(to_decimal(self.volume)))

        # Enforce OHLC price range invariants
        if self.high.amount < self.low.amount:
            raise ValidationError(
                f"OHLCV high price ({self.high.amount}) cannot be less than low price ({self.low.amount})."
            )
        if self.open.amount < self.low.amount or self.open.amount > self.high.amount:
            raise ValidationError(
                f"OHLCV open price ({self.open.amount}) outside [low, high] bounds."
            )
        if self.close.amount < self.low.amount or self.close.amount > self.high.amount:
            raise ValidationError(
                f"OHLCV close price ({self.close.amount}) outside [low, high] bounds."
            )

    def is_bullish(self) -> bool:
        """Return True if close > open."""
        return self.close.amount > self.open.amount

    def is_bearish(self) -> bool:
        """Return True if close < open."""
        return self.close.amount < self.open.amount

    def body_size_money(self) -> Money:
        """Return absolute body height (abs(close - open))."""
        return Money(
            amount=abs(self.close.amount - self.open.amount), currency=self.open.money.currency
        )

    def price_range(self) -> PriceRange:
        """Return PriceRange instance for this bar."""
        return PriceRange(low=self.low, high=self.high, open=self.open, close=self.close)

    def to_dict(self) -> dict[str, Any]:
        """Serialize OHLCV to dictionary."""
        return {
            "open": self.open.to_dict(),
            "high": self.high.to_dict(),
            "low": self.low.to_dict(),
            "close": self.close.to_dict(),
            "volume": self.volume.to_dict(),
            "is_bullish": self.is_bullish(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OHLCV":
        """Deserialize dictionary to OHLCV."""
        return cls(
            open=Price.from_dict(data["open"]),
            high=Price.from_dict(data["high"]),
            low=Price.from_dict(data["low"]),
            close=Price.from_dict(data["close"]),
            volume=Quantity.from_dict(data["volume"]),
        )


@dataclass(frozen=True, slots=True)
class Candle:
    """
    Immutable value object for a timeframe-bound OHLCV Candle.

    Attributes:
        timestamp (Timestamp): Candle open/start timestamp (UTC).
        timeframe (Timeframe): Bar timeframe granularity (1M, 5M, 1D, etc.).
        ohlcv (OHLCV): OHLCV data payload.
    """

    timestamp: Timestamp
    timeframe: Timeframe
    ohlcv: OHLCV

    def __post_init__(self) -> None:
        if not isinstance(self.timestamp, Timestamp):
            object.__setattr__(self, "timestamp", Timestamp(self.timestamp))
        if not isinstance(self.timeframe, Timeframe):
            object.__setattr__(self, "timeframe", Timeframe(self.timeframe))
        if not isinstance(self.ohlcv, OHLCV):
            raise ValidationError("Candle ohlcv attribute must be a valid OHLCV instance.")

    @property
    def open(self) -> Price:
        return self.ohlcv.open

    @property
    def high(self) -> Price:
        return self.ohlcv.high

    @property
    def low(self) -> Price:
        return self.ohlcv.low

    @property
    def close(self) -> Price:
        return self.ohlcv.close

    @property
    def volume(self) -> Quantity:
        return self.ohlcv.volume

    def is_bullish(self) -> bool:
        return self.ohlcv.is_bullish()

    def is_bearish(self) -> bool:
        return self.ohlcv.is_bearish()

    def to_dict(self) -> dict[str, Any]:
        """Serialize Candle to dictionary."""
        return {
            "timestamp": self.timestamp.to_dict(),
            "timeframe": self.timeframe.value,
            "ohlcv": self.ohlcv.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Candle":
        """Deserialize dictionary to Candle."""
        return cls(
            timestamp=Timestamp.from_dict(data["timestamp"]),
            timeframe=Timeframe(data["timeframe"]),
            ohlcv=OHLCV.from_dict(data["ohlcv"]),
        )
