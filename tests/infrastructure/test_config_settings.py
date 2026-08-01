"""
Unit tests for AppSettings Pydantic Settings configuration.
"""

import unittest

from packages.infrastructure.config import AppSettings, get_settings


class TestConfigSettings(unittest.TestCase):
    def test_app_settings_defaults(self) -> None:
        settings = AppSettings()
        self.assertEqual(settings.app_name, "Indian AI Hedge Fund Platform")
        self.assertEqual(settings.environment, "development")
        self.assertEqual(settings.database_url, "sqlite:///./app.db")
        self.assertFalse(settings.db_echo)
        self.assertEqual(settings.redis_url, "")
        self.assertEqual(settings.log_level, "INFO")
        self.assertEqual(settings.max_position_size_pct, 10.0)

    def test_get_settings_singleton(self) -> None:
        s1 = get_settings()
        s2 = get_settings()
        self.assertIs(s1, s2)


if __name__ == "__main__":
    unittest.main()
