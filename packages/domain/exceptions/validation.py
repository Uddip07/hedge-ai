"""
Validation Exceptions for the Indian AI Hedge Fund Domain.

Defines errors raised during domain value object, entity, or payload validation.
"""

from packages.domain.exceptions.base import DomainError


class ValidationError(DomainError):
    """Raised when a domain value object or input parameter fails validation rules."""

    DEFAULT_CODE = "VALIDATION_ERROR"


class OrderValidationError(ValidationError):
    """Raised when a trading order parameters fail pre-validation checks."""

    DEFAULT_CODE = "ORDER_VALIDATION_ERROR"


class PositionValidationError(ValidationError):
    """Raised when position parameters or sizing fail validation checks."""

    DEFAULT_CODE = "POSITION_VALIDATION_ERROR"


class TickerValidationError(ValidationError):
    """Raised when a ticker symbol format or exchange suffix is invalid."""

    DEFAULT_CODE = "TICKER_VALIDATION_ERROR"


class ISINValidationError(ValidationError):
    """Raised when an ISIN string fails structure or checksum validation."""

    DEFAULT_CODE = "ISIN_VALIDATION_ERROR"
