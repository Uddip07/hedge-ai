"""
Unit tests for System Domain Enums.
"""

import unittest

from packages.domain.enums.system import (
    BrokerType,
    CurrencyCode,
    NotificationPriority,
)


class TestSystemEnums(unittest.TestCase):
    """Test suite for System Enums."""

    def test_broker_type_helpers(self):
        self.assertTrue(BrokerType.DHAN.is_indian_broker())
        self.assertTrue(BrokerType.SHOONYA.is_indian_broker())
        self.assertTrue(BrokerType.ZERODHA.is_indian_broker())
        self.assertTrue(BrokerType.DHAN.supports_direct_api())

    def test_notification_priority_helpers(self):
        self.assertTrue(NotificationPriority.CRITICAL.is_urgent())
        self.assertFalse(NotificationPriority.LOW.is_urgent())

    def test_currency_code_helpers(self):
        self.assertEqual(CurrencyCode.INR.symbol(), "₹")
        self.assertEqual(CurrencyCode.USD.symbol(), "$")
        self.assertTrue(CurrencyCode.INR.is_inr())


if __name__ == "__main__":
    unittest.main()
