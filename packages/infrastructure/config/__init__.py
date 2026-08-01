"""
Infrastructure Configuration Package.

Exports AppSettings and get_settings factory function.
"""

from packages.infrastructure.config.settings import AppSettings, get_settings

__all__ = ["AppSettings", "get_settings"]
