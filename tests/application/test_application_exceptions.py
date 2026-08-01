"""
Unit tests for Application Layer Exception classes.
"""

import unittest

from packages.application.exceptions import (
    ApplicationError,
    ApplicationException,
    CommandExecutionError,
    EntityNotFoundApplicationError,
    PortError,
    QueryExecutionError,
    UnauthorizedApplicationError,
    ValidationApplicationError,
)


class TestApplicationExceptions(unittest.TestCase):
    def test_base_application_exception_initialization(self) -> None:
        err = ApplicationException("Test application error", context={"key": "val"})
        self.assertEqual(err.message, "Test application error")
        self.assertEqual(err.code, "APPLICATION_ERROR")
        self.assertEqual(err.context, {"key": "val"})
        self.assertIn("APPLICATION_ERROR", str(err))

        d = err.to_dict()
        self.assertEqual(d["error_type"], "ApplicationError")
        self.assertEqual(d["code"], "APPLICATION_ERROR")
        self.assertEqual(d["message"], "Test application error")
        self.assertEqual(d["context"], {"key": "val"})

    def test_application_exception_subclasses(self) -> None:
        cmd_err = CommandExecutionError("Command failed")
        self.assertEqual(cmd_err.code, "COMMAND_EXECUTION_ERROR")
        self.assertIsInstance(cmd_err, ApplicationError)

        qry_err = QueryExecutionError("Query failed")
        self.assertEqual(qry_err.code, "QUERY_EXECUTION_ERROR")

        port_err = PortError("Port connection failed")
        self.assertEqual(port_err.code, "PORT_ERROR")

        nf_err = EntityNotFoundApplicationError("Portfolio not found")
        self.assertEqual(nf_err.code, "ENTITY_NOT_FOUND")

        val_err = ValidationApplicationError("Invalid DTO field")
        self.assertEqual(val_err.code, "APPLICATION_VALIDATION_ERROR")

        unauth_err = UnauthorizedApplicationError("Access denied")
        self.assertEqual(unauth_err.code, "UNAUTHORIZED_APPLICATION_ERROR")


if __name__ == "__main__":
    unittest.main()
