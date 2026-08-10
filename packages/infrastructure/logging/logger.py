"""
Structured Logger for Infrastructure Layer.

Provides JSON structured logging formatting, contextual key-value logs,
and standard Python logging integration.
"""

import json
import logging
from datetime import UTC, datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """
    Custom Logging Formatter converting LogRecords to JSON strings.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "context") and isinstance(record.context, dict):
            log_data["context"] = record.context

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class StructuredLogger:
    """
    Structured Logger wrapper formatting contextual key-value logs.
    """

    def __init__(
        self,
        name: str = "indian_hedge_fund",
        level: str = "INFO",
        log_format: str = "json",
    ) -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self.logger.propagate = False

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            if log_format.lower() == "json":
                handler.setFormatter(JSONFormatter())
            else:
                handler.setFormatter(
                    logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s]: %(message)s")
                )
            self.logger.addHandler(handler)

    def info(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        exc_info: bool | Any = False,
    ) -> None:
        """Log info message with optional context dict."""
        self.logger.info(message, extra={"context": context or {}}, exc_info=exc_info)

    def warning(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        exc_info: bool | Any = False,
    ) -> None:
        """Log warning message with optional context dict."""
        self.logger.warning(message, extra={"context": context or {}}, exc_info=exc_info)

    def error(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        exc_info: bool | Any = False,
    ) -> None:
        """Log error message with optional context dict."""
        self.logger.error(message, extra={"context": context or {}}, exc_info=exc_info)

    def debug(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        exc_info: bool | Any = False,
    ) -> None:
        """Log debug message with optional context dict."""
        self.logger.debug(message, extra={"context": context or {}}, exc_info=exc_info)

    def critical(
        self,
        message: str,
        context: dict[str, Any] | None = None,
        exc_info: bool | Any = False,
    ) -> None:
        """Log critical message with optional context dict."""
        self.logger.critical(message, extra={"context": context or {}}, exc_info=exc_info)


def get_logger(
    name: str = "indian_hedge_fund",
    level: str = "INFO",
    log_format: str = "json",
) -> StructuredLogger:
    """Return a configured StructuredLogger instance."""
    return StructuredLogger(name=name, level=level, log_format=log_format)
