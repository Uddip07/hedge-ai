"""
Technical Indicator Value Objects for the Indian AI Hedge Fund Domain.

Provides ATR (Average True Range), RSI (Relative Strength Index), and MACD value objects.
Immutable, self-validating, and pure Decimal precision.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.domain.exceptions import ValidationError
from packages.domain.utils.math import to_decimal


@dataclass(frozen=True, slots=True)
class ATR:
    """
    Immutable value object for Average True Range (ATR) technical volatility indicator.

    Attributes:
        value (Decimal): Non-negative ATR price range value.
        period (int): Lookback period window (default 14).
    """

    value: Decimal
    period: int = 14

    def __post_init__(self) -> None:
        dec_val = to_decimal(self.value)
        if dec_val < Decimal("0"):
            raise ValidationError(
                f"ATR value cannot be negative. Got {dec_val}.",
                context={"value": str(dec_val)},
            )
        if self.period <= 0:
            raise ValidationError("ATR lookback period must be positive (> 0).")
        object.__setattr__(self, "value", dec_val)

    def to_dict(self) -> dict[str, Any]:
        """Serialize ATR to dictionary."""
        return {"value": str(self.value), "period": self.period}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ATR":
        """Deserialize dictionary to ATR."""
        return cls(value=Decimal(str(data["value"])), period=int(data.get("period", 14)))

    def __str__(self) -> str:
        return f"ATR({self.period})={self.value:.2f}"


@dataclass(frozen=True, slots=True)
class RSI:
    """
    Immutable value object for Relative Strength Index (RSI) technical momentum indicator [0, 100].

    Attributes:
        value (Decimal): RSI value bounded between 0.0 and 100.0.
        period (int): Lookback period window (default 14).
    """

    value: Decimal
    period: int = 14

    def __post_init__(self) -> None:
        dec_val = to_decimal(self.value)
        if dec_val < Decimal("0.0") or dec_val > Decimal("100.0"):
            raise ValidationError(
                f"RSI value must be bounded between 0.0 and 100.0. Got {dec_val}.",
                context={"value": str(dec_val)},
            )
        if self.period <= 0:
            raise ValidationError("RSI lookback period must be positive (> 0).")
        object.__setattr__(self, "value", dec_val)

    def is_overbought(self, threshold: Decimal = Decimal("70.0")) -> bool:
        """Return True if RSI >= overbought threshold (default 70.0)."""
        return self.value >= threshold

    def is_oversold(self, threshold: Decimal = Decimal("30.0")) -> bool:
        """Return True if RSI <= oversold threshold (default 30.0)."""
        return self.value <= threshold

    def to_dict(self) -> dict[str, Any]:
        """Serialize RSI to dictionary."""
        return {
            "value": str(self.value),
            "period": self.period,
            "is_overbought": self.is_overbought(),
            "is_oversold": self.is_oversold(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RSI":
        """Deserialize dictionary to RSI."""
        return cls(value=Decimal(str(data["value"])), period=int(data.get("period", 14)))

    def __str__(self) -> str:
        return f"RSI({self.period})={self.value:.2f}"


@dataclass(frozen=True, slots=True)
class MACD:
    """
    Immutable value object for Moving Average Convergence Divergence (MACD) indicator.

    Attributes:
        macd_line (Decimal): Fast EMA minus Slow EMA line.
        signal_line (Decimal): Signal line (EMA of MACD line).
        histogram (Decimal): MACD line minus Signal line.
        fast_period (int): Fast EMA window (default 12).
        slow_period (int): Slow EMA window (default 26).
        signal_period (int): Signal EMA window (default 9).
    """

    macd_line: Decimal
    signal_line: Decimal
    histogram: Decimal
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9

    def __post_init__(self) -> None:
        m_dec = to_decimal(self.macd_line)
        s_dec = to_decimal(self.signal_line)
        h_dec = to_decimal(self.histogram)
        object.__setattr__(self, "macd_line", m_dec)
        object.__setattr__(self, "signal_line", s_dec)
        object.__setattr__(self, "histogram", h_dec)

    def is_bullish(self) -> bool:
        """Return True if MACD line is above Signal line (histogram > 0)."""
        return self.histogram > Decimal("0")

    def is_bearish(self) -> bool:
        """Return True if MACD line is below Signal line (histogram < 0)."""
        return self.histogram < Decimal("0")

    def to_dict(self) -> dict[str, Any]:
        """Serialize MACD to dictionary."""
        return {
            "macd_line": str(self.macd_line),
            "signal_line": str(self.signal_line),
            "histogram": str(self.histogram),
            "fast_period": self.fast_period,
            "slow_period": self.slow_period,
            "signal_period": self.signal_period,
            "is_bullish": self.is_bullish(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MACD":
        """Deserialize dictionary to MACD."""
        return cls(
            macd_line=Decimal(str(data["macd_line"])),
            signal_line=Decimal(str(data["signal_line"])),
            histogram=Decimal(str(data["histogram"])),
            fast_period=int(data.get("fast_period", 12)),
            slow_period=int(data.get("slow_period", 26)),
            signal_period=int(data.get("signal_period", 9)),
        )

    def __str__(self) -> str:
        return (
            f"MACD({self.macd_line:.2f}, Signal={self.signal_line:.2f}, Hist={self.histogram:.2f})"
        )
