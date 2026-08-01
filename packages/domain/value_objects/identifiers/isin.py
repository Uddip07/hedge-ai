"""
ISIN Value Object for the Indian AI Hedge Fund Domain.

Represents an International Securities Identification Number (ISIN).
Immutable, self-validating with Luhn checksum verification.
"""

from dataclasses import dataclass
from typing import Any

from packages.domain.utils.validation import validate_isin_checksum


@dataclass(frozen=True, slots=True)
class ISIN:
    """
    Immutable value object for an ISIN code (e.g. 'INE002A01018').

    Attributes:
        value (str): 12-character checksum-validated ISIN string.
    """

    value: str

    def __post_init__(self) -> None:
        validated = validate_isin_checksum(self.value)
        object.__setattr__(self, "value", validated)

    @property
    def country_code(self) -> str:
        """Return 2-alpha ISO country code prefix (e.g., 'IN' for India)."""
        return self.value[:2]

    @property
    def national_id(self) -> str:
        """Return 9-character national security identifier payload."""
        return self.value[2:11]

    @property
    def check_digit(self) -> str:
        """Return final Luhn check digit."""
        return self.value[11]

    def is_indian(self) -> bool:
        """Return True if this is an Indian ISIN ('IN' prefix)."""
        return self.country_code == "IN"

    def to_dict(self) -> dict[str, Any]:
        """Serialize value object to dictionary."""
        return {"isin": self.value, "country_code": self.country_code}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ISIN":
        """Deserialize dictionary to ISIN value object."""
        return cls(value=data["isin"])

    def __str__(self) -> str:
        return self.value
