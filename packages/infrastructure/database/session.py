"""
SQLAlchemy 2.x Database Session and Engine Infrastructure.

Provides DeclarativeBase, Engine factory, SessionFactory, and DatabaseManager lifecycle manager.
"""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from packages.infrastructure.database.config import DatabaseConfig


class Base(DeclarativeBase):
    """
    SQLAlchemy 2.x Declarative Base Class for ORM Mappings.
    """


def create_db_engine(config: DatabaseConfig | None = None) -> Engine:
    """
    Construct a SQLAlchemy 2.x Engine instance from DatabaseConfig parameters.

    Args:
        config (DatabaseConfig | None): Database configuration options.

    Returns:
        Engine: Initialized SQLAlchemy Engine instance.
    """
    cfg = config or DatabaseConfig()
    is_sqlite = cfg.url.startswith("sqlite")

    connect_args = dict(cfg.connect_args)
    if is_sqlite:
        connect_args.setdefault("check_same_thread", False)
        if cfg.url in ("sqlite:///:memory:", "sqlite://"):
            from sqlalchemy.pool import StaticPool

            return create_engine(
                cfg.url,
                echo=cfg.echo,
                connect_args=connect_args,
                poolclass=StaticPool,
            )
        return create_engine(
            cfg.url,
            echo=cfg.echo,
            connect_args=connect_args,
        )

    return create_engine(
        cfg.url,
        echo=cfg.echo,
        pool_size=cfg.pool_size,
        max_overflow=cfg.max_overflow,
        pool_pre_ping=cfg.pool_pre_ping,
        connect_args=connect_args,
    )


def get_session_factory(engine: Engine) -> sessionmaker[Session]:
    """
    Construct a SQLAlchemy sessionmaker factory bound to an Engine.

    Args:
        engine (Engine): Initialized SQLAlchemy Engine instance.

    Returns:
        sessionmaker[Session]: Configured session factory.
    """
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class DatabaseManager:
    """
    Database Lifecycle Manager wrapping Engine and SessionFactory creation.

    Provides database schema creation, session scoping, and cleanup.
    """

    def __init__(self, config: DatabaseConfig | None = None) -> None:
        self.config = config or DatabaseConfig()
        self.engine = create_db_engine(self.config)
        self.session_factory = get_session_factory(self.engine)

    def create_all(self) -> None:
        """Create all declarative database tables."""
        Base.metadata.create_all(self.engine)

    def drop_all(self) -> None:
        """Drop all declarative database tables."""
        Base.metadata.drop_all(self.engine)

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        Provide a transactional session context manager.

        Yields:
            Session: Active SQLAlchemy Session instance.
        """
        sess = self.session_factory()
        try:
            yield sess
            sess.commit()
        except Exception:
            sess.rollback()
            raise
        finally:
            sess.close()
