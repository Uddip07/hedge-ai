"""
Unit tests for StructuredLogger logging infrastructure.
"""

import unittest

from packages.infrastructure.logging import StructuredLogger, get_logger


class TestLoggingInfrastructure(unittest.TestCase):
    def test_structured_logger_formatting(self) -> None:
        logger = get_logger(name="test_logger", level="DEBUG", log_format="json")
        self.assertIsInstance(logger, StructuredLogger)

        # Ensure logging methods don't throw exceptions
        logger.info("Info log message", context={"user_id": "123"})
        logger.warning("Warning log message", context={"retries": 2})
        logger.error("Error log message", context={"error_code": "ERR_500"})
        logger.debug("Debug log message")
        logger.critical("Critical log message")


if __name__ == "__main__":
    unittest.main()
