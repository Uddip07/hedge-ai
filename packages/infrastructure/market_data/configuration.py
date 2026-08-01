"""
Market Data Infrastructure Configuration.

Defines configuration settings for Market Data providers, caching, retries, and rate limits.
"""

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MarketDataConfig:
    """
    Configuration model for Market Intelligence Infrastructure.
    """

    default_provider: str = field(
        default_factory=lambda: os.getenv("MARKET_DATA_PROVIDER", "yahoo")
    )
    timeout_sec: int = field(default_factory=lambda: int(os.getenv("MARKET_DATA_TIMEOUT", "30")))
    cache_enabled: bool = field(
        default_factory=lambda: (
            os.getenv("MARKET_DATA_CACHE", "true").lower() in ("true", "1", "yes")
        )
    )

    max_retries: int = field(default_factory=lambda: int(os.getenv("MARKET_DATA_MAX_RETRIES", "3")))
    rate_limit_per_min: int = field(
        default_factory=lambda: int(os.getenv("MARKET_DATA_RATE_LIMIT", "300"))
    )
