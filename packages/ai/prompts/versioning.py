"""
Prompt Version Manager for Prompt Intelligence Framework.

Tracks prompt template version numbers, changelogs, and version lookup resolution.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from packages.domain.enums.ai import AgentType


@dataclass(frozen=True)
class PromptVersionEntry:
    """
    Historical version release entry for a prompt template.
    """

    version: str
    changelog: str
    release_date: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class PromptVersionManager:
    """
    Manager maintaining version release logs and version string comparisons.
    """

    def __init__(self) -> None:
        self._history: dict[AgentType, list[PromptVersionEntry]] = {}

    def record_version(self, agent_type: AgentType, version: str, changelog: str) -> None:
        """Log a new prompt version release."""
        if agent_type not in self._history:
            self._history[agent_type] = []
        self._history[agent_type].append(PromptVersionEntry(version=version, changelog=changelog))

    def get_version_history(self, agent_type: AgentType) -> list[dict[str, Any]]:
        """Retrieve version history for an agent type."""
        entries = self._history.get(agent_type, [])
        return [
            {
                "version": e.version,
                "changelog": e.changelog,
                "release_date": e.release_date,
            }
            for e in entries
        ]

    def is_valid_version(self, version: str) -> bool:
        """Check if a version string complies with semantic versioning (X.Y.Z)."""
        parts = version.split(".")
        return len(parts) == 3 and all(p.isdigit() for p in parts)
