"""
Score Metrics Value Objects for the Indian AI Hedge Fund Domain.

Provides RiskScore, ConfidenceScore, and RecommendationScore value objects.
Immutable, self-validating, and bound to core domain enums.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from packages.domain.enums.research import RecommendationType
from packages.domain.enums.risk import RiskLevel
from packages.domain.exceptions import ValidationError
from packages.domain.utils.math import to_decimal
from packages.domain.value_objects.core.percentage import Percentage


@dataclass(frozen=True, slots=True)
class RiskScore:
    """
    Immutable value object for risk assessment intensity scores [0.0, 1.0].

    Attributes:
        value (Decimal): Risk score bounded between 0.0 (minimal risk) and 1.0 (unacceptable risk).
    """

    value: Decimal

    def __post_init__(self) -> None:
        dec_val = to_decimal(self.value)
        if dec_val < Decimal("0.0") or dec_val > Decimal("1.0"):
            raise ValidationError(
                f"RiskScore must be bounded between 0.0 and 1.0. Got {dec_val}.",
                context={"value": str(dec_val)},
            )
        object.__setattr__(self, "value", dec_val)

    def as_percentage(self) -> Percentage:
        """Return score as a Percentage instance."""
        return Percentage.from_ratio(self.value)

    def risk_level(self) -> RiskLevel:
        """Map numeric score to domain RiskLevel enum."""
        if self.value < Decimal("0.2"):
            return RiskLevel.LOW
        elif self.value < Decimal("0.5"):
            return RiskLevel.MEDIUM
        elif self.value < Decimal("0.8"):
            return RiskLevel.HIGH
        elif self.value < Decimal("0.95"):
            return RiskLevel.CRITICAL
        return RiskLevel.UNACCEPTABLE

    def to_dict(self) -> dict[str, Any]:
        """Serialize RiskScore to dictionary."""
        return {
            "value": str(self.value),
            "level": self.risk_level().value,
            "percentage": str(self.as_percentage()),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RiskScore":
        """Deserialize dictionary to RiskScore."""
        return cls(value=Decimal(str(data["value"])))

    def __str__(self) -> str:
        return f"RiskScore({self.value:.2f} - {self.risk_level().value})"


@dataclass(frozen=True, slots=True)
class ConfidenceScore:
    """
    Immutable value object for AI or quantitative model confidence scores [0.0, 1.0].

    Attributes:
        value (Decimal): Confidence score between 0.0 (zero confidence) and 1.0 (full confidence).
    """

    value: Decimal

    def __post_init__(self) -> None:
        dec_val = to_decimal(self.value)
        if dec_val < Decimal("0.0") or dec_val > Decimal("1.0"):
            raise ValidationError(
                f"ConfidenceScore must be bounded between 0.0 and 1.0. Got {dec_val}.",
                context={"value": str(dec_val)},
            )
        object.__setattr__(self, "value", dec_val)

    def as_percentage(self) -> Percentage:
        """Return score as a Percentage instance."""
        return Percentage.from_ratio(self.value)

    def is_high_confidence(self, threshold: Decimal = Decimal("0.75")) -> bool:
        """Return True if confidence meets or exceeds threshold (default 0.75)."""
        return self.value >= threshold

    def to_dict(self) -> dict[str, Any]:
        """Serialize ConfidenceScore to dictionary."""
        return {
            "value": str(self.value),
            "percentage": str(self.as_percentage()),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConfidenceScore":
        """Deserialize dictionary to ConfidenceScore."""
        return cls(value=Decimal(str(data["value"])))

    def __str__(self) -> str:
        return f"{self.as_percentage()}"


@dataclass(frozen=True, slots=True)
class RecommendationScore:
    """
    Immutable value object for research recommendation ratings [-1.0, 1.0].
    -1.0 = Strong Sell, 0.0 = Hold, +1.0 = Strong Buy.

    Attributes:
        value (Decimal): Recommendation rating bounded between -1.0 and +1.0.
    """

    value: Decimal

    def __post_init__(self) -> None:
        dec_val = to_decimal(self.value)
        if dec_val < Decimal("-1.0") or dec_val > Decimal("1.0"):
            raise ValidationError(
                f"RecommendationScore must be bounded between -1.0 and +1.0. Got {dec_val}.",
                context={"value": str(dec_val)},
            )
        object.__setattr__(self, "value", dec_val)

    def recommendation_type(self) -> RecommendationType:
        """Map score to RecommendationType enum."""
        if self.value >= Decimal("0.6"):
            return RecommendationType.STRONG_BUY
        elif self.value >= Decimal("0.2"):
            return RecommendationType.BUY
        elif self.value > Decimal("-0.2"):
            return RecommendationType.HOLD
        elif self.value > Decimal("-0.6"):
            return RecommendationType.SELL
        return RecommendationType.STRONG_SELL

    def to_dict(self) -> dict[str, Any]:
        """Serialize RecommendationScore to dictionary."""
        return {
            "value": str(self.value),
            "type": self.recommendation_type().value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecommendationScore":
        """Deserialize dictionary to RecommendationScore."""
        return cls(value=Decimal(str(data["value"])))

    def __str__(self) -> str:
        return f"Recommendation({self.value:+.2f} - {self.recommendation_type().value})"
