"""
Market Data Infrastructure Exceptions.

Defines infrastructure-level exceptions for market data providers, category registries,
retry policies, validation filters, and capability/feature enforcement.
"""

from typing import Any


class MarketDataError(Exception):
    """Base exception class for all Market Data Infrastructure errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class FeatureNotSupportedError(MarketDataError):
    """Raised explicitly when a requested market data feature is not supported by a provider."""


class ProviderCapabilityError(MarketDataError):
    """Raised when a provider lacks a required capability for an operation or category."""


class ProviderConnectionError(MarketDataError):
    """Raised when a transient network connection error occurs with a provider API."""


class ProviderTimeoutError(MarketDataError):
    """Raised when a market data request times out."""


class DataNotFoundError(MarketDataError):
    """Raised when requested market data is not available for a ticker or timeframe."""


class ValidationMarketDataError(MarketDataError):
    """Raised when raw provider responses fail payload validation (malformed/corrupted data)."""


class RateLimitError(MarketDataError):
    """Raised when an API rate limit is exceeded for a provider."""
