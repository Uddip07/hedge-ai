"""
Unit tests for Domain Exceptions.
"""

import unittest

import packages.domain.exceptions as domain_exceptions
from packages.domain.exceptions import (
    DomainError,
    InsufficientFundsError,
    OrderValidationError,
    PortfolioError,
    RiskViolation,
    ValidationError,
)


class TestDomainExceptions(unittest.TestCase):
    """Test suite for Domain Exception hierarchy."""

    def test_base_domain_error_initialization(self):
        err = DomainError(
            message="Test error occurred",
            code="CUSTOM_CODE",
            context={"symbol": "RELIANCE.NSE", "price": 2500.0},
            metadata={"user": "admin"},
        )
        self.assertEqual(err.message, "Test error occurred")
        self.assertEqual(err.code, "CUSTOM_CODE")
        self.assertEqual(err.context["symbol"], "RELIANCE.NSE")
        self.assertIn("timestamp", err.metadata)

    def test_domain_error_serialization(self):
        err = DomainError(message="Invalid trade", context={"trade_id": "T123"})
        err_dict = err.to_dict()
        self.assertEqual(err_dict["error"], "DomainError")
        self.assertEqual(err_dict["code"], "DOMAIN_ERROR")
        self.assertEqual(err_dict["message"], "Invalid trade")
        self.assertEqual(err_dict["context"]["trade_id"], "T123")

    def test_domain_error_str_representation(self):
        err_no_ctx = DomainError("Simple message")
        self.assertEqual(str(err_no_ctx), "[DOMAIN_ERROR] Simple message")

        err_with_ctx = DomainError("Message", context={"key": "val"})
        self.assertIn("[DOMAIN_ERROR] Message (key=val)", str(err_with_ctx))

    def test_subclass_hierarchy_and_default_codes(self):
        err_val = ValidationError("Validation failed")
        self.assertTrue(isinstance(err_val, DomainError))
        self.assertEqual(err_val.code, "VALIDATION_ERROR")

        err_order = OrderValidationError("Order invalid")
        self.assertTrue(isinstance(err_order, ValidationError))
        self.assertEqual(err_order.code, "ORDER_VALIDATION_ERROR")

        err_funds = InsufficientFundsError(
            "Not enough cash", context={"required": 1000, "available": 500}
        )
        self.assertTrue(isinstance(err_funds, PortfolioError))
        self.assertEqual(err_funds.code, "INSUFFICIENT_FUNDS")

        err_risk = RiskViolation("Max drawdown exceeded")
        self.assertTrue(isinstance(err_risk, DomainError))
        self.assertEqual(err_risk.code, "RISK_VIOLATION")

    def test_all_exceptions_export_completeness(self):
        exported_names = domain_exceptions.__all__
        self.assertGreaterEqual(len(exported_names), 20)

        for name in exported_names:
            cls = getattr(domain_exceptions, name)
            self.assertTrue(issubclass(cls, DomainError))
            instance = cls("Test message")
            self.assertIsNotNone(instance.code)
            self.assertIsNotNone(instance.to_dict())


if __name__ == "__main__":
    unittest.main()
