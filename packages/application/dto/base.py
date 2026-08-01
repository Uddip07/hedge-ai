"""
Base Data Transfer Object (DTO) Abstraction.

DTOs carry serializable structured data across application boundary layers.
Pure application value objects with zero infrastructure dependencies.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BaseDTO(ABC):
    """
    Abstract Base Class for all Application Data Transfer Objects (DTOs).

    DTOs decouple internal domain aggregate representations from boundary inputs/outputs.
    """

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize DTO to dictionary format."""

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseDTO":
        """Deserialize dictionary to DTO instance."""
