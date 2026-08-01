"""
Application Exceptions Package.

Exports application-level error base classes and sub-exceptions.
"""

from packages.application.exceptions.base import (
    ApplicationError,
    ApplicationException,
    CommandExecutionError,
    EntityNotFoundApplicationError,
    PortError,
    QueryExecutionError,
    UnauthorizedApplicationError,
    ValidationApplicationError,
)

__all__ = [
    "ApplicationError",
    "ApplicationException",
    "CommandExecutionError",
    "EntityNotFoundApplicationError",
    "PortError",
    "QueryExecutionError",
    "UnauthorizedApplicationError",
    "ValidationApplicationError",
]
