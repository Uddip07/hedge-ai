"""
Execution Gateway & Broker Exceptions for the Indian AI Hedge Fund Domain.

Defines domain errors arising from order routing and broker interaction limits.
"""

from packages.domain.exceptions.base import DomainError


class ExecutionError(DomainError):
    """Base exception for trade execution gateway and routing failures."""

    DEFAULT_CODE = "EXECUTION_ERROR"


class BrokerError(ExecutionError):
    """Raised when broker abstraction layer rejects an operation or loses connection."""

    DEFAULT_CODE = "BROKER_ERROR"
