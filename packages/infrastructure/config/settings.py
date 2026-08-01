"""
Infrastructure Settings powered by Pydantic Settings.

Defines typed configuration settings for Database, Cache, Logging, and Risk limits.
Reads environment variables prefixed with 'APP_'.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """
    Application & Infrastructure configuration model.

    Attributes:
        app_name (str): Application platform name.
        environment (str): Operational environment (development, staging, production).
        debug (bool): Enable debug diagnostics flag.
        database_url (str): SQLAlchemy database connection string (default SQLite in-memory).
        db_echo (bool): Enable SQL query logging echo.
        db_pool_size (int): Connection pool size for DB engines.
        db_max_overflow (int): Maximum connection pool overflow limit.
        redis_url (str): Redis cache connection URL string.
        cache_enabled (bool): Global cache activation flag.
        cache_default_ttl (int): Default cache TTL in seconds.
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR).
        log_format (str): Structured logging format (json, text).
        max_position_size_pct (float): Maximum single position size percentage.
        max_sector_concentration_pct (float): Maximum sector concentration percentage.
    """

    app_name: str = Field(default="Indian AI Hedge Fund Platform")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)

    # Database Settings
    database_url: str = Field(default="sqlite:///./app.db")
    db_echo: bool = Field(default=False)
    db_pool_size: int = Field(default=5)
    db_max_overflow: int = Field(default=10)

    # Redis / Cache Settings
    redis_url: str = Field(default="")
    cache_enabled: bool = Field(default=True)
    cache_default_ttl: int = Field(default=300)

    # Structured Logging Settings
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    # Risk Policy Limits
    max_position_size_pct: float = Field(default=10.0)
    max_sector_concentration_pct: float = Field(default=25.0)

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> AppSettings:
    """Return cached AppSettings singleton instance."""
    return AppSettings()
