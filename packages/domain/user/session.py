"""
User Session Domain Entity.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any

from packages.domain.value_objects.identifiers.uuid_wrappers import UserId
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass
class UserSession:
    """
    Represents an active or revoked user login session / refresh token.
    """

    user_id: UserId
    refresh_token_hash: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    user_agent: str = ""
    ip_address: str = ""
    is_revoked: bool = False
    expires_at: Timestamp = field(default_factory=Timestamp.now_utc)
    created_at: Timestamp = field(default_factory=Timestamp.now_utc)

    @property
    def is_expired(self) -> bool:
        return Timestamp.now_utc().value >= self.expires_at.value

    @property
    def is_valid(self) -> bool:
        return not self.is_revoked and not self.is_expired

    def revoke(self) -> None:
        self.is_revoked = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "refresh_token_hash": self.refresh_token_hash,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
            "is_revoked": self.is_revoked,
            "expires_at": self.expires_at.iso_format,
            "created_at": self.created_at.iso_format,
        }
