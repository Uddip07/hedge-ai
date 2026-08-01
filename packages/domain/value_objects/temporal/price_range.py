"""
PriceRange Value Object for the Indian AI Hedge Fund Domain.

Represents an OHLC or High/Low price range interval. Immutable and self-validating.
"""

from dataclasses import dataclass
from typing import Any

from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.core.price import Price


@dataclass(frozen=True, slots=True)
class PriceRange:
    """
    Immutable value object for price range boundaries.

    Attributes:
        low (Price): Low price boundary.
        high (Price): High price boundary.
        open (Optional[Price]): Opening price.
        close (Optional[Price]): Closing price.
    """

    low: Price
    high: Price
    open: Price | None = None
    close: Price | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.low, Price) or not isinstance(self.high, Price):
            raise ValidationError("PriceRange low and high must be valid Price instances.")

        if self.low.amount > self.high.amount:
            raise ValidationError(
                f"PriceRange low price ({self.low.amount}) cannot exceed high price ({self.high.amount}).",
                context={"low": str(self.low.amount), "high": str(self.high.amount)},
            )

        # Enforce currency consistency
        if self.low.money.currency != self.high.money.currency:
            raise ValidationError("PriceRange low and high must share the same currency.")

        if self.open is not None:
            if not isinstance(self.open, Price):
                raise ValidationError("PriceRange open must be a valid Price instance.")
            if self.open.money.currency != self.low.money.currency:
                raise ValidationError("PriceRange open must share the same currency.")
            if self.open.amount < self.low.amount or self.open.amount > self.high.amount:
                raise ValidationError(
                    f"PriceRange open price ({self.open.amount}) outside [low, high] bounds.",
                    context={"open": str(self.open.amount)},
                )

        if self.close is not None:
            if not isinstance(self.close, Price):
                raise ValidationError("PriceRange close must be a valid Price instance.")
            if self.close.money.currency != self.low.money.currency:
                raise ValidationError("PriceRange close must share the same currency.")
            if self.close.amount < self.low.amount or self.close.amount > self.high.amount:
                raise ValidationError(
                    f"PriceRange close price ({self.close.amount}) outside [low, high] bounds.",
                    context={"close": str(self.close.amount)},
                )

    @property
    def spread_money(self) -> Money:
        """Return the absolute price spread as a Money instance."""
        return self.high.money - self.low.money

    def contains(self, price: Price) -> bool:
        """Return True if the given price falls within [low, high] inclusive."""
        if price.money.currency != self.low.money.currency:
            return False
        return self.low.amount <= price.amount <= self.high.amount

    def to_dict(self) -> dict[str, Any]:
        """Serialize PriceRange to dictionary."""
        return {
            "low": self.low.to_dict(),
            "high": self.high.to_dict(),
            "open": self.open.to_dict() if self.open else None,
            "close": self.close.to_dict() if self.close else None,
            "spread": self.spread_money.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PriceRange":
        """Deserialize dictionary to PriceRange."""
        low = Price.from_dict(data["low"])
        high = Price.from_dict(data["high"])
        open_price = Price.from_dict(data["open"]) if data.get("open") else None
        close_price = Price.from_dict(data["close"]) if data.get("close") else None
        return cls(low=low, high=high, open=open_price, close=close_price)

    def __str__(self) -> str:
        return f"[{self.low} - {self.high}]"
