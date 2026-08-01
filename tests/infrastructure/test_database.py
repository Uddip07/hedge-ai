"""
Unit tests for SQLAlchemy 2.x Database Infrastructure.
"""

import unittest

from sqlalchemy import text

from packages.infrastructure.database import (
    DatabaseConfig,
    DatabaseManager,
    create_db_engine,
    get_session_factory,
)


class TestDatabaseInfrastructure(unittest.TestCase):
    def test_database_config_defaults(self) -> None:
        cfg = DatabaseConfig()
        self.assertEqual(cfg.url, "sqlite:///:memory:")
        self.assertFalse(cfg.echo)
        self.assertEqual(cfg.pool_size, 5)

    def test_create_db_engine_and_session_factory(self) -> None:
        cfg = DatabaseConfig(url="sqlite:///:memory:", echo=False)
        engine = create_db_engine(cfg)
        factory = get_session_factory(engine)
        self.assertIsNotNone(engine)

        with factory() as session:
            res = session.execute(text("SELECT 1")).scalar()
            self.assertEqual(res, 1)

    def test_database_manager_lifecycle(self) -> None:
        mgr = DatabaseManager(DatabaseConfig(url="sqlite:///:memory:"))
        mgr.create_all()

        with mgr.session() as sess:
            self.assertTrue(sess.is_active)

        mgr.drop_all()


if __name__ == "__main__":
    unittest.main()
