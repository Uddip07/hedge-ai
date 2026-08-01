"""
Unit tests for Domain Validation Helpers.
"""

import unittest
from decimal import Decimal

from packages.domain.exceptions import (
    ISINValidationError,
    TickerValidationError,
    ValidationError,
)
from packages.domain.utils.validation import (
    validate_isin_checksum,
    validate_non_negative_decimal,
    validate_percentage_range,
    validate_positive_decimal,
    validate_ticker_format,
)


class TestValidationUtils(unittest.TestCase):
    """Test suite for validation utilities."""

    def test_validate_ticker_format_success(self):
        self.assertEqual(validate_ticker_format("RELIANCE"), "RELIANCE")
        self.assertEqual(validate_ticker_format("reliance.nse"), "RELIANCE.NSE")
        self.assertEqual(validate_ticker_format("INFY:NSE"), "INFY.NSE")

    def test_validate_ticker_format_failures(self):
        with self.assertRaises(TickerValidationError):
            validate_ticker_format("")
        with self.assertRaises(TickerValidationError):
            validate_ticker_format("INVALID_TICKER_SYMBOL_TOO_LONG_EXTENDED")

    def test_validate_isin_checksum_success(self):
        # Valid Reliance ISIN
        self.assertEqual(validate_isin_checksum("INE002A01018"), "INE002A01018")
        # Valid Apple ISIN
        self.assertEqual(validate_isin_checksum("US0378331005"), "US0378331005")

    def test_validate_isin_checksum_failures(self):
        with self.assertRaises(ISINValidationError):
            validate_isin_checksum("INVALID_ISIN")
        with self.assertRaises(ISINValidationError):
            validate_isin_checksum("INE002A01019")  # Bad check digit

    def test_validate_positive_decimal(self):
        self.assertEqual(validate_positive_decimal("10.5"), Decimal("10.5"))
        with self.assertRaises(ValidationError):
            validate_positive_decimal("0")
        with self.assertRaises(ValidationError):
            validate_positive_decimal("-5.0")
        with self.assertRaises(ValidationError):
            validate_positive_decimal("abc")

    def test_validate_non_negative_decimal(self):
        self.assertEqual(validate_non_negative_decimal("0"), Decimal("0"))
        self.assertEqual(validate_non_negative_decimal("100"), Decimal("100"))
        with self.assertRaises(ValidationError):
            validate_non_negative_decimal("-0.01")

    def test_validate_percentage_range(self):
        self.assertEqual(validate_percentage_range("50"), Decimal("50"))
        self.assertEqual(validate_percentage_range("0"), Decimal("0"))
        self.assertEqual(validate_percentage_range("100"), Decimal("100"))
        with self.assertRaises(ValidationError):
            validate_percentage_range("-1")
        with self.assertRaises(ValidationError):
            validate_percentage_range("100.1")


if __name__ == "__main__":
    unittest.main()
