"""
Base Domain Error for the Indian AI Hedge Fund Platform.

Defines the root Exception class for all domain errors, guaranteeing structured error codes,
contextual payloads, metadata, and serialization. Zero infrastructure dependencies.
"""

from datetime import UTC, datetime
from typing import Any


class DomainError(Exception):
    """
    Base exception class for all domain errors.

    Attributes:
        message (str): Human-readable error description.
        code (str): Machine-readable error code identifier.
        context (Dict[str, Any]): Domain contextual parameters when the error occurred.
        metadata (Dict[str, Any]): Additional operational metadata (e.g., timestamp).
    """

    DEFAULT_CODE = "DOMAIN_ERROR"

    def __init__(
        self,
        message: str,
        code: str | None = None,
        context: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.DEFAULT_CODE
        self.context = context or {}
        self.metadata = metadata or {}

        # Automatically attach UTC timestamp if missing
        if "timestamp" not in self.metadata:
            self.metadata["timestamp"] = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Return a structured dictionary representation of the error."""
        return {
            "error": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "context": self.context,
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"[{self.code}] {self.message} ({context_str})"
        return f"[{self.code}] {self.message}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"code={self.code!r}, "
            f"context={self.context!r})"
        )
