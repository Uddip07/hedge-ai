"""
Market Infrastructure Exceptions for the Indian AI Hedge Fund Domain.

Defines errors related to market session state, corporate action processing, and trade settlement.
"""

from packages.domain.exceptions.base import DomainError


class MarketError(DomainError):
    """Base exception for financial market and exchange data/session errors."""

    DEFAULT_CODE = "MARKET_ERROR"


class CorporateActionError(MarketError):
    """Raised when processing a corporate action event (splits, dividends) fails."""

    DEFAULT_CODE = "CORPORATE_ACTION_ERROR"


class SettlementError(MarketError):
    """Raised when trade clearing or T+1 settlement verification fails."""

    DEFAULT_CODE = "SETTLEMENT_ERROR"
