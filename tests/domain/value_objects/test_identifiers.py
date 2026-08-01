"""
Unit tests for Identifier Value Objects (Ticker, ISIN, Currency, Typed UUIDs).
"""

import unittest
import uuid

from packages.domain.enums.market import ExchangeType
from packages.domain.enums.system import CurrencyCode
from packages.domain.exceptions import ISINValidationError, ValidationError
from packages.domain.value_objects.identifiers import (
    ISIN,
    Currency,
    OrderId,
    PortfolioId,
    Ticker,
    TradeId,
)


class TestIdentifierValueObjects(unittest.TestCase):
    """Test suite for Ticker, ISIN, Currency, and Typed UUID value objects."""

    def test_ticker_valid_instantiation_and_properties(self):
        t1 = Ticker("RELIANCE", ExchangeType.NSE)
        self.assertEqual(t1.symbol, "RELIANCE")
        self.assertEqual(t1.exchange, ExchangeType.NSE)
        self.assertEqual(t1.full_symbol, "RELIANCE.NSE")
        self.assertTrue(t1.is_indian())

        # Test string parsing format "INFY.NSE"
        t2 = Ticker("INFY.NSE")
        self.assertEqual(t2.symbol, "INFY")
        self.assertEqual(t2.exchange, ExchangeType.NSE)
        self.assertEqual(t2.full_symbol, "INFY.NSE")

    def test_ticker_immutability_and_equality(self):
        t1 = Ticker("RELIANCE", ExchangeType.NSE)
        t2 = Ticker("RELIANCE", ExchangeType.NSE)
        self.assertEqual(t1, t2)
        self.assertEqual(hash(t1), hash(t2))

        with self.assertRaises(AttributeError):
            t1.symbol = "TATAMOTORS"  # type: ignore

    def test_ticker_serialization(self):
        t = Ticker("TCS", ExchangeType.BSE)
        t_dict = t.to_dict()
        self.assertEqual(t_dict["symbol"], "TCS")
        self.assertEqual(t_dict["exchange"], "BSE")

        t_restored = Ticker.from_dict(t_dict)
        self.assertEqual(t, t_restored)

    def test_isin_validation_and_properties(self):
        # Valid Reliance ISIN
        isin = ISIN("INE002A01018")
        self.assertEqual(isin.value, "INE002A01018")
        self.assertEqual(isin.country_code, "IN")
        self.assertEqual(isin.national_id, "E002A0101")
        self.assertEqual(isin.check_digit, "8")
        self.assertTrue(isin.is_indian())

        # Invalid checksum
        with self.assertRaises(ISINValidationError):
            ISIN("INE002A01019")

    def test_isin_serialization(self):
        isin = ISIN("US0378331005")
        isin_dict = isin.to_dict()
        self.assertEqual(isin_dict["isin"], "US0378331005")
        self.assertEqual(isin_dict["country_code"], "US")

        restored = ISIN.from_dict(isin_dict)
        self.assertEqual(isin, restored)

    def test_currency_value_object(self):
        c1 = Currency(CurrencyCode.INR)
        self.assertEqual(c1.code, CurrencyCode.INR)
        self.assertEqual(c1.symbol, "₹")
        self.assertTrue(c1.is_inr())

        c2 = Currency.from_dict({"code": "USD"})
        self.assertEqual(c2.symbol, "$")
        self.assertFalse(c2.is_inr())

    def test_typed_uuid_wrappers(self):
        order_id_1 = OrderId.generate()
        order_id_2 = OrderId.from_str(str(order_id_1.value))
        self.assertEqual(order_id_1, order_id_2)

        portfolio_id = PortfolioId.generate()
        self.assertNotEqual(order_id_1.value, portfolio_id.value)

        # Ensure OrderId and TradeId with same UUID value are unequal (type distinction)
        raw_uuid = uuid.uuid4()
        oid = OrderId(raw_uuid)
        tid = TradeId(raw_uuid)
        self.assertNotEqual(oid, tid)

        # Invalid UUID string
        with self.assertRaises(ValidationError):
            OrderId.from_str("invalid-uuid-string")


if __name__ == "__main__":
    unittest.main()
