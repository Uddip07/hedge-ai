"""
Unit tests for Core Value Objects (Money, Price, Percentage, Quantity, Weight, Allocation, SectorWeight).
"""

import unittest
from decimal import Decimal

from packages.domain.enums.market import MarketSegment
from packages.domain.enums.system import CurrencyCode
from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.core import (
    Allocation,
    Money,
    Percentage,
    Price,
    Quantity,
    SectorWeight,
    Weight,
)
from packages.domain.value_objects.identifiers import Currency, Ticker


class TestCoreValueObjects(unittest.TestCase):
    """Test suite for Money, Price, Percentage, Quantity, Weight, Allocation, SectorWeight."""

    def test_money_arithmetic_and_rounding(self):
        m1 = Money(Decimal("100.50"))
        m2 = Money(Decimal("50.25"))
        self.assertEqual((m1 + m2).amount, Decimal("150.75"))
        self.assertEqual((m1 - m2).amount, Decimal("50.25"))
        self.assertEqual((m1 * 2).amount, Decimal("201.00"))
        self.assertEqual((m1 / 2).amount, Decimal("50.25"))

        # Currency mismatch error
        m_usd = Money(Decimal("100"), Currency(CurrencyCode.USD))
        with self.assertRaises(ValidationError):
            _ = m1 + m_usd

    def test_money_allocate(self):
        m = Money(Decimal("100.00"))
        # Allocate 1:1:1 across 3 buckets -> 33.34, 33.33, 33.33 (total 100.00)
        allocations = m.allocate([1, 1, 1])
        self.assertEqual(len(allocations), 3)
        total = sum(a.amount for a in allocations)
        self.assertEqual(total, Decimal("100.00"))

    def test_price_validation_and_arithmetic(self):
        p1 = Price.from_amount(2500)
        p2 = Price.from_amount(500)
        self.assertEqual(p1.amount, Decimal("2500"))
        self.assertEqual((p1 + p2).amount, Decimal("3000"))

        with self.assertRaises(ValidationError):
            Price.from_amount(-10)  # Negative price rejected

    def test_percentage_properties_and_clamping(self):
        pct = Percentage(Decimal("15.5"))
        self.assertEqual(pct.to_ratio(), Decimal("0.155"))

        pct_over = Percentage(Decimal("120"))
        self.assertEqual(pct_over.normalize().value, Decimal("100"))

        pct_under = Percentage(Decimal("-10"))
        self.assertEqual(pct_under.normalize().value, Decimal("0"))

    def test_quantity_properties(self):
        q_int = Quantity(Decimal("100"))
        self.assertTrue(q_int.is_integer())
        self.assertEqual(str(q_int), "100")

        q_frac = Quantity(Decimal("10.5"))
        self.assertFalse(q_frac.is_integer())

        with self.assertRaises(ValidationError):
            Quantity(Decimal("-5"))

    def test_weight_ratio_validation(self):
        w = Weight(Decimal("0.25"))
        self.assertEqual(w.as_percentage().value, Decimal("25.0"))

        with self.assertRaises(ValidationError):
            Weight(Decimal("1.5"))  # Out of range [0.0, 1.0]

    def test_allocation_value_object(self):
        t = Ticker("RELIANCE.NSE")
        w = Weight(Decimal("0.10"))
        alloc = Allocation(ticker=t, weight=w)
        self.assertEqual(alloc.ticker, t)
        self.assertEqual(alloc.weight, w)
        self.assertIsNone(alloc.target_money)

        m = Money(Decimal("100000"))
        alloc_with_m = alloc.with_target_money(m)
        self.assertEqual(alloc_with_m.target_money, m)

    def test_sector_weight_value_object(self):
        sw = SectorWeight(sector=MarketSegment.LARGE_CAP, weight=Weight(Decimal("0.40")))
        self.assertEqual(sw.sector, MarketSegment.LARGE_CAP)
        self.assertEqual(sw.weight.ratio, Decimal("0.40"))

        sw_dict = sw.to_dict()
        restored = SectorWeight.from_dict(sw_dict)
        self.assertEqual(sw, restored)


if __name__ == "__main__":
    unittest.main()
