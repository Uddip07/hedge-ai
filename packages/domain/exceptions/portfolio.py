"""
Portfolio Exceptions for the Indian AI Hedge Fund Domain.

Defines errors related to portfolio accounting, position limits, and cash balance availability.
"""

from packages.domain.exceptions.base import DomainError


class PortfolioError(DomainError):
    """Base exception for portfolio aggregate state errors."""

    DEFAULT_CODE = "PORTFOLIO_ERROR"


class InsufficientFundsError(PortfolioError):
    """Raised when available portfolio buying power is insufficient for an order or allocation."""

    DEFAULT_CODE = "INSUFFICIENT_FUNDS"
