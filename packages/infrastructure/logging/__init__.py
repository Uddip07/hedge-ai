"""
Infrastructure Logging Package.

Exports StructuredLogger and get_logger factory function.
"""

from packages.infrastructure.logging.logger import StructuredLogger, get_logger

__all__ = ["StructuredLogger", "get_logger"]
