"""
Currency Value Object for the Indian AI Hedge Fund Domain.

Represents an ISO-4217 Currency, wrapping CurrencyCode enum. Immutable and self-validating.
"""

from dataclasses import dataclass
from typing import Any

from packages.domain.enums.system import CurrencyCode
from packages.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class Currency:
    """
    Immutable value object for fiat currencies.

    Attributes:
        code (CurrencyCode): ISO-4217 currency code enum (default CurrencyCode.INR).
    """

    code: CurrencyCode = CurrencyCode.INR

    def __post_init__(self) -> None:
        if not isinstance(self.code, CurrencyCode):
            try:
                object.__setattr__(self, "code", CurrencyCode(self.code))
            except ValueError as exc:
                raise ValidationError(
                    f"Invalid CurrencyCode: '{self.code}'.",
                    context={"currency": str(self.code)},
                ) from exc

    @property
    def symbol(self) -> str:
        """Return currency display symbol (e.g. '₹', '$')."""
        return self.code.symbol()

    def is_inr(self) -> bool:
        """Return True if this currency is Indian Rupee (INR)."""
        return self.code.is_inr()

    def to_dict(self) -> dict[str, Any]:
        """Serialize currency to dictionary."""
        return {"code": self.code.value, "symbol": self.symbol}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Currency":
        """Deserialize dictionary to Currency value object."""
        return cls(code=CurrencyCode(data["code"]))

    def __str__(self) -> str:
        return self.code.value
