"""
Risk Management Exceptions for the Indian AI Hedge Fund Domain.

Defines errors raised when mandates, stop loss, VaR limits, or circuit breakers are breached.
"""

from packages.domain.exceptions.base import DomainError


class RiskViolation(DomainError):
    """Raised when a trade or portfolio allocation breaches risk mandates or safety limits."""

    DEFAULT_CODE = "RISK_VIOLATION"
