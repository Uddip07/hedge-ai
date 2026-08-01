"""
Database Configuration for SQLAlchemy 2.x Infrastructure.

Provides DatabaseConfig encapsulation for engine and session parameters.
"""

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DatabaseConfig:
    """
    Configuration parameters for SQLAlchemy 2.x Engine and SessionFactory initialization.

    Attributes:
        url (str): Connection string URL.
        echo (bool): SQL statement echo logging flag.
        pool_size (int): Connection pool capacity.
        max_overflow (int): Connection pool max overflow.
        pool_pre_ping (bool): Validate connection health before checkout.
    """

    url: str = field(default="")
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_pre_ping: bool = True
    connect_args: dict[str, bool] = field(default_factory=dict)
    market_data_path: str = field(default="")

    def __post_init__(self) -> None:
        if not self.url:
            pg_user = os.getenv("POSTGRES_USER")
            pg_pass = os.getenv("POSTGRES_PASSWORD")
            pg_host = os.getenv("POSTGRES_HOST")
            pg_port = os.getenv("POSTGRES_PORT", "5432")
            pg_db = os.getenv("POSTGRES_DATABASE")
            app_db = os.getenv("APP_DATABASE_URL")

            if pg_host and pg_db and pg_user:
                constructed_url = (
                    f"postgresql+psycopg2://{pg_user}:{pg_pass or ''}@{pg_host}:{pg_port}/{pg_db}"
                )
                object.__setattr__(self, "url", constructed_url)
            elif app_db:
                object.__setattr__(self, "url", app_db)
            else:
                object.__setattr__(self, "url", "sqlite:///./app.db")

        if not self.market_data_path:
            mdp = os.getenv("MARKET_DATA_PATH", "./MarketData")
            object.__setattr__(self, "market_data_path", mdp)
