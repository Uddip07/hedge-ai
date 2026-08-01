"""
Base Command Abstraction for CQRS Architecture.

Commands represent write/mutation intents in the CQRS pattern.
Pure application value objects with zero infrastructure dependencies.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any

from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, kw_only=True)
class BaseCommand:
    """
    Abstract Base Class for all CQRS Write Commands.

    Commands encapsulate input data necessary to mutate domain state or execute business operations.

    Attributes:
        command_id (uuid.UUID): Unique command invocation identifier.
        timestamp (Timestamp): Point-in-time timestamp of command creation (UTC).
        user_id (uuid.UUID | None): Optional user/actor ID initiating the command.
    """

    command_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: Timestamp = field(default_factory=Timestamp.now_utc)
    user_id: uuid.UUID | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.command_id, uuid.UUID):
            object.__setattr__(self, "command_id", uuid.UUID(str(self.command_id)))
        if not isinstance(self.timestamp, Timestamp):
            object.__setattr__(self, "timestamp", Timestamp(self.timestamp))
        if self.user_id is not None and not isinstance(self.user_id, uuid.UUID):
            object.__setattr__(self, "user_id", uuid.UUID(str(self.user_id)))

    @property
    def command_name(self) -> str:
        """Return canonical class name of the command."""
        return self.__class__.__name__

    def to_dict(self) -> dict[str, Any]:
        """Serialize BaseCommand to dictionary format."""
        return {
            "command_name": self.command_name,
            "command_id": str(self.command_id),
            "timestamp": self.timestamp.isoformat(),
            "user_id": str(self.user_id) if self.user_id else None,
        }
