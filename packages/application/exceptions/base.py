"""
Base Application Exceptions for the Indian AI Hedge Fund Platform.

Defines the ApplicationException hierarchy for handling application-level failure modes.
Pure application exceptions with zero external infrastructure dependencies.
"""

from typing import Any


class ApplicationError(Exception):
    """
    Root base exception for all Application Layer errors.

    Attributes:
        message (str): Human-readable error message.
        code (str): Machine-readable error code string.
        context (dict[str, Any]): Additional structured error context data.
    """

    DEFAULT_CODE = "APPLICATION_ERROR"

    def __init__(
        self,
        message: str,
        code: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.DEFAULT_CODE
        self.context = context or {}

    def to_dict(self) -> dict[str, Any]:
        """Serialize ApplicationError to dictionary format."""
        return {
            "error_type": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "context": self.context,
        }

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


# Canonical alias mandated by platform architecture
ApplicationException = ApplicationError


class CommandExecutionError(ApplicationError):
    """Raised when an application command handler fails to execute a Command."""

    DEFAULT_CODE = "COMMAND_EXECUTION_ERROR"


class QueryExecutionError(ApplicationError):
    """Raised when an application query handler fails to execute a Query."""

    DEFAULT_CODE = "QUERY_EXECUTION_ERROR"


class PortError(ApplicationError):
    """Base exception for external port communication or invocation failures."""

    DEFAULT_CODE = "PORT_ERROR"


class EntityNotFoundApplicationError(ApplicationError):
    """Raised when a requested domain entity is not found during application use case execution."""

    DEFAULT_CODE = "ENTITY_NOT_FOUND"


class ValidationApplicationError(ApplicationError):
    """Raised when input command/query validation fails at the application boundary."""

    DEFAULT_CODE = "APPLICATION_VALIDATION_ERROR"


class UnauthorizedApplicationError(ApplicationError):
    """Raised when an application action is unauthorized for the current request context."""

    DEFAULT_CODE = "UNAUTHORIZED_APPLICATION_ERROR"
