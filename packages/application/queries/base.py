"""
Base Query Abstraction for CQRS Architecture.

Queries represent read-only requests in the CQRS pattern.
Pure application value objects with zero infrastructure dependencies.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any

from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass(frozen=True, kw_only=True)
class BaseQuery:
    """
    Abstract Base Class for all CQRS Read Queries.

    Queries encapsulate request filter parameters for side-effect-free data retrieval.

    Attributes:
        query_id (uuid.UUID): Unique query invocation identifier.
        timestamp (Timestamp): Point-in-time timestamp of query creation (UTC).
        user_id (uuid.UUID | None): Optional user/actor ID initiating the query.
    """

    query_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: Timestamp = field(default_factory=Timestamp.now_utc)
    user_id: uuid.UUID | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.query_id, uuid.UUID):
            object.__setattr__(self, "query_id", uuid.UUID(str(self.query_id)))
        if not isinstance(self.timestamp, Timestamp):
            object.__setattr__(self, "timestamp", Timestamp(self.timestamp))
        if self.user_id is not None and not isinstance(self.user_id, uuid.UUID):
            object.__setattr__(self, "user_id", uuid.UUID(str(self.user_id)))

    @property
    def query_name(self) -> str:
        """Return canonical class name of the query."""
        return self.__class__.__name__

    def to_dict(self) -> dict[str, Any]:
        """Serialize BaseQuery to dictionary format."""
        return {
            "query_name": self.query_name,
            "query_id": str(self.query_id),
            "timestamp": self.timestamp.isoformat(),
            "user_id": str(self.user_id) if self.user_id else None,
        }
