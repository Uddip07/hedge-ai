"""
Domain Utilities Package for the Indian AI Hedge Fund Platform.

Consolidates validation and financial math helpers.
"""

from packages.domain.utils.math import (
    calculate_cagr,
    calculate_drawdown,
    calculate_return,
    calculate_sharpe_ratio,
    round_currency,
    to_decimal,
)
from packages.domain.utils.validation import (
    validate_isin_checksum,
    validate_non_negative_decimal,
    validate_percentage_range,
    validate_positive_decimal,
    validate_ticker_format,
)

__all__ = [
    # Validation helpers
    "validate_ticker_format",
    "validate_isin_checksum",
    "validate_positive_decimal",
    "validate_non_negative_decimal",
    "validate_percentage_range",
    # Math helpers
    "to_decimal",
    "round_currency",
    "calculate_return",
    "calculate_drawdown",
    "calculate_sharpe_ratio",
    "calculate_cagr",
]
