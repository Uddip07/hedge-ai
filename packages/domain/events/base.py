"""
Base DomainEvent for the Indian AI Hedge Fund Platform.

Defines the abstract frozen DomainEvent base class. Pure domain model with zero infrastructure.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any

from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """
    Abstract Base Class for all Domain Events.

    Domain Events represent immutable facts that have already occurred within the system.

    Attributes:
        aggregate_id (str): Identifier of the originating aggregate root entity.
        event_id (uuid.UUID): Unique event identifier.
        occurred_at (Timestamp): Timestamp when the event occurred (UTC).
        version (int): Domain event schema version number.
    """

    aggregate_id: str
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: Timestamp = field(default_factory=Timestamp.now_utc)
    version: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.occurred_at, Timestamp):
            object.__setattr__(self, "occurred_at", Timestamp(self.occurred_at))

    @property
    def event_type(self) -> str:
        """Return canonical class name of the domain event."""
        return self.__class__.__name__

    def to_dict(self) -> dict[str, Any]:
        """Serialize DomainEvent to dictionary."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_at": self.occurred_at.to_dict(),
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DomainEvent":
        """Deserialize dictionary to DomainEvent."""
        return cls(
            event_id=uuid.UUID(data["event_id"]),
            aggregate_id=data["aggregate_id"],
            occurred_at=Timestamp.from_dict(data["occurred_at"]),
            version=int(data.get("version", 1)),
        )
