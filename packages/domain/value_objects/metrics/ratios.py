"""
Ratio Metrics Value Objects for the Indian AI Hedge Fund Domain.

Provides SharpeRatio, SortinoRatio, Drawdown, and Volatility value objects.
Immutable, self-validating, and pure Decimal precision.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.domain.exceptions import ValidationError
from packages.domain.utils.math import round_currency, to_decimal
from packages.domain.value_objects.core.percentage import Percentage


@dataclass(frozen=True, slots=True)
class SharpeRatio:
    """
    Immutable value object for Sharpe Ratio (risk-adjusted return per unit of total risk).

    Attributes:
        value (Decimal): Calculated Sharpe Ratio.
    """

    value: Decimal

    def __post_init__(self) -> None:
        dec_val = to_decimal(self.value)
        object.__setattr__(self, "value", dec_val)

    def is_acceptable(self) -> bool:
        """Return True if Sharpe Ratio >= 1.0."""
        return self.value >= Decimal("1.0")

    def is_excellent(self) -> bool:
        """Return True if Sharpe Ratio >= 2.0."""
        return self.value >= Decimal("2.0")

    def rounded(self, decimals: int = 2) -> "SharpeRatio":
        """Return rounded SharpeRatio."""
        return SharpeRatio(value=round_currency(self.value, decimals=decimals))

    def to_dict(self) -> dict[str, Any]:
        """Serialize SharpeRatio to dictionary."""
        return {"value": str(self.value), "is_acceptable": self.is_acceptable()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SharpeRatio":
        """Deserialize dictionary to SharpeRatio."""
        return cls(value=Decimal(str(data["value"])))

    def __str__(self) -> str:
        return f"{self.value:.2f}"


@dataclass(frozen=True, slots=True)
class SortinoRatio:
    """
    Immutable value object for Sortino Ratio (risk-adjusted return per unit of downside risk).

    Attributes:
        value (Decimal): Calculated Sortino Ratio.
    """

    value: Decimal

    def __post_init__(self) -> None:
        dec_val = to_decimal(self.value)
        object.__setattr__(self, "value", dec_val)

    def is_acceptable(self) -> bool:
        """Return True if Sortino Ratio >= 1.5."""
        return self.value >= Decimal("1.5")

    def rounded(self, decimals: int = 2) -> "SortinoRatio":
        """Return rounded SortinoRatio."""
        return SortinoRatio(value=round_currency(self.value, decimals=decimals))

    def to_dict(self) -> dict[str, Any]:
        """Serialize SortinoRatio to dictionary."""
        return {"value": str(self.value), "is_acceptable": self.is_acceptable()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SortinoRatio":
        """Deserialize dictionary to SortinoRatio."""
        return cls(value=Decimal(str(data["value"])))

    def __str__(self) -> str:
        return f"{self.value:.2f}"


@dataclass(frozen=True, slots=True)
class Drawdown:
    """
    Immutable value object for peak-to-trough equity drawdown percentage [0, 100].

    Attributes:
        percentage (Percentage): Drawdown percentage value object.
    """

    percentage: Percentage

    def __post_init__(self) -> None:
        if not isinstance(self.percentage, Percentage):
            object.__setattr__(self, "percentage", Percentage(to_decimal(self.percentage)))
        if self.percentage.value < Decimal("0") or self.percentage.value > Decimal("100"):
            raise ValidationError(
                f"Drawdown percentage must be between 0% and 100%. Got {self.percentage.value}%.",
                context={"percentage": str(self.percentage.value)},
            )

    @classmethod
    def from_value(cls, val: Any) -> "Drawdown":
        """Construct Drawdown directly from float/int/str/Decimal percentage value."""
        return cls(percentage=Percentage(to_decimal(val)))

    @property
    def value(self) -> Decimal:
        """Return raw Decimal drawdown percentage."""
        return self.percentage.value

    def is_breached(self, max_limit: Percentage) -> bool:
        """Return True if drawdown exceeds the mandated safety limit."""
        return self.percentage > max_limit

    def to_dict(self) -> dict[str, Any]:
        """Serialize Drawdown to dictionary."""
        return {"percentage": self.percentage.to_dict()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Drawdown":
        """Deserialize dictionary to Drawdown."""
        return cls(percentage=Percentage.from_dict(data["percentage"]))

    def __str__(self) -> str:
        return f"{self.percentage}"


@dataclass(frozen=True, slots=True)
class Volatility:
    """
    Immutable value object for annualized volatility percentage (standard deviation of returns).

    Attributes:
        percentage (Percentage): Volatility percentage value object.
    """

    percentage: Percentage

    def __post_init__(self) -> None:
        if not isinstance(self.percentage, Percentage):
            object.__setattr__(self, "percentage", Percentage(to_decimal(self.percentage)))
        if self.percentage.value < Decimal("0"):
            raise ValidationError(
                f"Volatility percentage cannot be negative. Got {self.percentage.value}%.",
                context={"percentage": str(self.percentage.value)},
            )

    @classmethod
    def from_value(cls, val: Any) -> "Volatility":
        """Construct Volatility directly from numeric value."""
        return cls(percentage=Percentage(to_decimal(val)))

    @property
    def value(self) -> Decimal:
        """Return raw Decimal volatility percentage."""
        return self.percentage.value

    def to_dict(self) -> dict[str, Any]:
        """Serialize Volatility to dictionary."""
        return {"percentage": self.percentage.to_dict()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Volatility":
        """Deserialize dictionary to Volatility."""
        return cls(percentage=Percentage.from_dict(data["percentage"]))

    def __str__(self) -> str:
        return f"{self.percentage}"
