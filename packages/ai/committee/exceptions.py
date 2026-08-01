"""
Exceptions for Intelligent Investment Committee Engine.

Defines standardized domain exceptions for planning, task graph, scheduling,
critique, judgement, and investment memory operations.
"""

from typing import Any


class CommitteeError(Exception):
    """
    Base Exception for all Intelligent Investment Committee errors.

    Attributes:
        message (str): Explanatory error message.
        details (dict[str, Any]): Contextual metadata.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class PlanningError(CommitteeError):
    """Raised when request intent parsing or research plan generation fails."""


class TaskGraphError(CommitteeError):
    """Raised when task graph dependency construction or cycle detection fails."""


class SchedulerError(CommitteeError):
    """Raised when task graph execution, dependency resolution, or timeout occurs."""


class CritiqueError(CommitteeError):
    """Raised when critic evaluation or contradiction analysis fails."""


class JudgementError(CommitteeError):
    """Raised when judge evidence quality or confidence assessment fails."""


class MemoryError(CommitteeError):
    """Raised when persistent investment reasoning memory operations fail."""
