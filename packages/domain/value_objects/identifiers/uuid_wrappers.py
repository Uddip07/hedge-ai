"""
Typed UUID Value Objects for the Indian AI Hedge Fund Domain.

Provides strongly typed, immutable UUID wrapper value objects for aggregate entities
and domain events. Guarantees type safety and prevents ID mismatch bugs across contexts.
"""

import uuid
from dataclasses import dataclass
from typing import Any, TypeVar

from packages.domain.exceptions import ValidationError

T = TypeVar("T", bound="EntityId")


@dataclass(frozen=True, slots=True)
class EntityId:
    """
    Base immutable UUID value object wrapper for domain entities.

    Attributes:
        value (uuid.UUID): 128-bit UUID instance.
    """

    value: uuid.UUID

    def __post_init__(self) -> None:
        if isinstance(self.value, str):
            try:
                object.__setattr__(self, "value", uuid.UUID(self.value))
            except ValueError as exc:
                raise ValidationError(
                    f"Invalid UUID string for {self.__class__.__name__}: '{self.value}'",
                    context={"id_type": self.__class__.__name__, "raw_val": str(self.value)},
                ) from exc
        elif not isinstance(self.value, uuid.UUID):
            raise ValidationError(
                f"{self.__class__.__name__} value must be a valid UUID or UUID hex string.",
                context={"id_type": self.__class__.__name__, "type": type(self.value).__name__},
            )

    @classmethod
    def generate(cls: type[T]) -> T:
        """Factory method to generate a new random UUID v4 identifier."""
        return cls(value=uuid.uuid4())

    @classmethod
    def from_str(cls: type[T], val_str: str) -> T:
        """Parse string to typed EntityId."""
        try:
            return cls(value=uuid.UUID(val_str))
        except (ValueError, TypeError) as exc:
            raise ValidationError(
                f"Invalid UUID string for {cls.__name__}: '{val_str}'",
                context={"id_type": cls.__name__, "raw_val": str(val_str)},
            ) from exc

    def to_dict(self) -> dict[str, Any]:
        """Serialize ID value object to dictionary."""
        return {"id": str(self.value), "type": self.__class__.__name__}

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """Deserialize dictionary payload to EntityId."""
        try:
            return cls(value=uuid.UUID(data["id"]))
        except (ValueError, TypeError, KeyError) as exc:
            raise ValidationError(
                f"Invalid UUID payload for {cls.__name__}: '{data}'",
                context={"id_type": cls.__name__, "data": data},
            ) from exc

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class OrderId(EntityId):
    """Strongly-typed Order Identifier."""


@dataclass(frozen=True, slots=True)
class TradeId(EntityId):
    """Strongly-typed Trade Identifier."""


@dataclass(frozen=True, slots=True)
class PortfolioId(EntityId):
    """Strongly-typed Portfolio Aggregate Root Identifier."""


@dataclass(frozen=True, slots=True)
class ResearchId(EntityId):
    """Strongly-typed Research Report Aggregate Root Identifier."""


@dataclass(frozen=True, slots=True)
class StrategyId(EntityId):
    """Strongly-typed Quantitative Strategy Aggregate Root Identifier."""


@dataclass(frozen=True, slots=True)
class BacktestId(EntityId):
    """Strongly-typed Backtest Run Aggregate Root Identifier."""


@dataclass(frozen=True, slots=True)
class BrokerId(EntityId):
    """Strongly-typed Broker Account Aggregate Root Identifier."""


@dataclass(frozen=True, slots=True)
class UserId(EntityId):
    """Strongly-typed User Identifier."""


@dataclass(frozen=True, slots=True)
class PromptId(EntityId):
    """Strongly-typed LLM Prompt Identifier."""


@dataclass(frozen=True, slots=True)
class DocumentId(EntityId):
    """Strongly-typed Knowledge Document Identifier."""


@dataclass(frozen=True, slots=True)
class ExecutionId(EntityId):
    """Strongly-typed Execution Task Identifier."""
