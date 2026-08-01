"""
Unit tests for Domain Financial Math Helpers.
"""

import unittest
from decimal import Decimal

from packages.domain.exceptions import ValidationError
from packages.domain.utils.math import (
    calculate_cagr,
    calculate_drawdown,
    calculate_return,
    calculate_sharpe_ratio,
    round_currency,
    to_decimal,
)


class TestMathUtils(unittest.TestCase):
    """Test suite for financial math utilities."""

    def test_to_decimal(self):
        self.assertEqual(to_decimal(10), Decimal("10"))
        self.assertEqual(to_decimal("10.55"), Decimal("10.55"))
        self.assertEqual(to_decimal(10.55), Decimal("10.55"))
        self.assertEqual(to_decimal(Decimal("10.55")), Decimal("10.55"))
        with self.assertRaises(ValidationError):
            to_decimal("invalid_number")

    def test_round_currency(self):
        self.assertEqual(round_currency(Decimal("100.456")), Decimal("100.46"))
        self.assertEqual(round_currency(Decimal("100.454")), Decimal("100.45"))
        self.assertEqual(round_currency(Decimal("100.455")), Decimal("100.46"))

    def test_calculate_return(self):
        self.assertEqual(calculate_return(Decimal("100"), Decimal("120")), Decimal("20.0000"))
        self.assertEqual(calculate_return(Decimal("100"), Decimal("80")), Decimal("-20.0000"))
        with self.assertRaises(ValidationError):
            calculate_return(Decimal("0"), Decimal("100"))

    def test_calculate_drawdown(self):
        # 100 peak to 80 current -> 20% drawdown
        self.assertEqual(calculate_drawdown(Decimal("80"), Decimal("100")), Decimal("20.0000"))
        # 100 peak to 120 current -> 0% drawdown
        self.assertEqual(calculate_drawdown(Decimal("120"), Decimal("100")), Decimal("0.0000"))

    def test_calculate_sharpe_ratio(self):
        # mean=15%, rf=5%, std=10% -> (15-5)/10 = 1.0
        self.assertEqual(
            calculate_sharpe_ratio(Decimal("15"), Decimal("5"), Decimal("10")),
            Decimal("1.0000"),
        )
        with self.assertRaises(ValidationError):
            calculate_sharpe_ratio(Decimal("15"), Decimal("5"), Decimal("0"))

    def test_calculate_cagr(self):
        # 100 to 200 in 3 years -> ~25.9921%
        cagr = calculate_cagr(Decimal("100"), Decimal("200"), Decimal("3"))
        self.assertAlmostEqual(float(cagr), 25.9921, places=2)
        with self.assertRaises(ValidationError):
            calculate_cagr(Decimal("0"), Decimal("200"), Decimal("3"))
        with self.assertRaises(ValidationError):
            calculate_cagr(Decimal("100"), Decimal("200"), Decimal("0"))


if __name__ == "__main__":
    unittest.main()
