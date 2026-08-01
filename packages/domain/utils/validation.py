"""
Domain Validation Helpers for the Indian AI Hedge Fund Platform.

Provides shared, reusable validation routines for ticker symbols, ISIN checksums,
and Decimal numeric range boundaries. Zero infrastructure dependencies.
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Any

from packages.domain.exceptions import (
    ISINValidationError,
    TickerValidationError,
    ValidationError,
)

# Standard Ticker pattern: 1-15 uppercase alphanumeric chars optional dot/colon exchange suffix
_TICKER_REGEX = re.compile(r"^[A-Z0-9]{1,15}(?:[\.:][A-Z]{2,10})?$")

# Standard ISIN pattern: 2 alpha country code + 9 alphanumeric + 1 check digit
_ISIN_REGEX = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$")


def validate_ticker_format(ticker: str) -> str:
    """
    Validate and normalize a ticker symbol (e.g., 'RELIANCE', 'RELIANCE.NSE', 'INFY:NSE').

    Returns:
        str: Normalized uppercase ticker string.

    Raises:
        TickerValidationError: If format is invalid or empty.
    """
    if not isinstance(ticker, str) or not ticker.strip():
        raise TickerValidationError("Ticker symbol must be a non-empty string.")

    cleaned = ticker.strip().upper().replace(":", ".")
    if not _TICKER_REGEX.match(cleaned):
        raise TickerValidationError(
            f"Invalid ticker format: '{ticker}'. Expected e.g. 'RELIANCE' or 'RELIANCE.NSE'.",
            context={"raw_ticker": ticker},
        )
    return cleaned


def validate_isin_checksum(isin: str) -> str:
    """
    Validate an International Securities Identification Number (ISIN) including Luhn checksum.
    e.g. 'INE002A01018' (Reliance Industries Ltd).

    Returns:
        str: Normalized uppercase ISIN string.

    Raises:
        ISINValidationError: If format or checksum is invalid.
    """
    if not isinstance(isin, str) or not isin.strip():
        raise ISINValidationError("ISIN must be a non-empty string.")

    cleaned = isin.strip().upper()
    if not _ISIN_REGEX.match(cleaned):
        raise ISINValidationError(
            f"Invalid ISIN format: '{isin}'. Expected 12-character alphanumeric code.",
            context={"raw_isin": isin},
        )

    # Convert ISIN letters to numbers (A=10, B=11, ..., Z=35)
    digits_str = ""
    for char in cleaned[:-1]:
        if char.isalpha():
            digits_str += str(ord(char) - 55)
        else:
            digits_str += char
    digits_str += cleaned[-1]

    # Double every second digit from right to left
    total = 0
    reverse_digits = [int(d) for d in reversed(digits_str[:-1])]
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 0:
            doubled = digit * 2
            total += (doubled // 10) + (doubled % 10)
        else:
            total += digit

    # Compute check digit
    check_digit = (10 - (total % 10)) % 10
    actual_check_digit = int(cleaned[-1])

    if check_digit != actual_check_digit:
        raise ISINValidationError(
            f"ISIN check digit mismatch for '{isin}'. Computed {check_digit}, got {actual_check_digit}.",
            context={
                "raw_isin": isin,
                "expected": check_digit,
                "actual": actual_check_digit,
            },
        )

    return cleaned


def to_decimal(val: Any) -> Decimal:
    """Convert Value Object, float, int, str, or Decimal to Decimal safely."""
    if hasattr(val, "value"):
        return Decimal(str(val.value))
    if hasattr(val, "amount"):
        return Decimal(str(val.amount))
    return Decimal(str(val))


def validate_positive_decimal(val: Any, field_name: str = "value") -> Decimal:
    """
    Validate and convert a value to a strictly positive Decimal (> 0).

    Raises:
        ValidationError: If value <= 0 or non-numeric.
    """
    try:
        dec = Decimal(str(val))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError(
            f"Field '{field_name}' must be a valid numeric Decimal.",
            context={"field": field_name, "val": str(val)},
        ) from exc

    if dec <= Decimal("0"):
        raise ValidationError(
            f"Field '{field_name}' must be strictly positive (> 0). Got {dec}.",
            context={"field": field_name, "value": str(dec)},
        )
    return dec


def validate_non_negative_decimal(val: Any, field_name: str = "value") -> Decimal:
    """
    Validate and convert a value to a non-negative Decimal (>= 0).

    Raises:
        ValidationError: If value < 0 or non-numeric.
    """
    try:
        dec = Decimal(str(val))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError(
            f"Field '{field_name}' must be a valid numeric Decimal.",
            context={"field": field_name, "val": str(val)},
        ) from exc

    if dec < Decimal("0"):
        raise ValidationError(
            f"Field '{field_name}' must be non-negative (>= 0). Got {dec}.",
            context={"field": field_name, "value": str(dec)},
        )
    return dec


def validate_percentage_range(
    val: Any,
    field_name: str = "percentage",
    min_pct: Decimal = Decimal("0"),
    max_pct: Decimal = Decimal("100"),
) -> Decimal:
    """
    Validate and convert a percentage value to Decimal within range [min_pct, max_pct].

    Raises:
        ValidationError: If value is outside range or non-numeric.
    """
    try:
        dec = Decimal(str(val))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError(
            f"Field '{field_name}' must be a valid numeric Decimal.",
            context={"field": field_name, "val": str(val)},
        ) from exc

    if dec < min_pct or dec > max_pct:
        raise ValidationError(
            f"Field '{field_name}' must be between {min_pct}% and {max_pct}%. Got {dec}%.",
            context={
                "field": field_name,
                "value": str(dec),
                "min": str(min_pct),
                "max": str(max_pct),
            },
        )
    return dec
