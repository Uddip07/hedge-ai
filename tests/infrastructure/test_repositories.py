"""
Unit tests for SQL Repositories.
"""

import unittest
from decimal import Decimal

from packages.domain.enums.portfolio import PortfolioType
from packages.domain.enums.trading import AssetType
from packages.domain.market.asset import Asset
from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.research.report import ResearchReport
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.identifiers import PortfolioId, Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import ResearchId
from packages.infrastructure.repositories import (
    SQLAssetRepository,
    SQLPortfolioRepository,
    SQLResearchRepository,
)


class TestRepositoriesInfrastructure(unittest.TestCase):
    def test_sql_portfolio_repository_crud(self) -> None:
        repo = SQLPortfolioRepository()
        p_id = PortfolioId.generate()
        port = Portfolio(
            id=p_id,
            name="Infrastructure Portfolio",
            portfolio_type=PortfolioType.PAPER,
            cash_balance=Money(Decimal("50000.00")),
        )

        self.assertIsNone(repo.get_by_id(p_id))
        repo.save(port)

        fetched = repo.get_by_id(p_id)
        self.assertIsNotNone(fetched)
        assert fetched is not None
        self.assertEqual(fetched.name, "Infrastructure Portfolio")
        self.assertEqual(len(repo.list_all()), 1)

        repo.delete(p_id)
        self.assertIsNone(repo.get_by_id(p_id))

    def test_sql_asset_repository_crud(self) -> None:
        repo = SQLAssetRepository()
        t = Ticker("RELIANCE.NSE")
        asset = Asset(
            name="Reliance Industries Limited",
            ticker=t,
            asset_type=AssetType.EQUITY,
        )

        self.assertIsNone(repo.get_by_id(asset.id))
        repo.save(asset)

        fetched = repo.get_by_id(asset.id)
        self.assertIsNotNone(fetched)
        assert fetched is not None
        self.assertEqual(fetched.name, "Reliance Industries Limited")

        fetched_t = repo.get_by_ticker(t)
        self.assertIsNotNone(fetched_t)
        assert fetched_t is not None
        self.assertEqual(fetched_t.id, asset.id)

        repo.delete(asset.id)
        self.assertIsNone(repo.get_by_id(asset.id))

    def test_sql_research_repository_crud(self) -> None:
        repo = SQLResearchRepository()
        r_id = ResearchId.generate()
        t = Ticker("TCS.NSE")
        report = ResearchReport(id=r_id, ticker=t)

        repo.save(report)
        fetched = repo.get_by_id(r_id)
        self.assertIsNotNone(fetched)
        assert fetched is not None
        self.assertEqual(fetched.ticker, t)

        fetched_t = repo.get_by_ticker(t)
        self.assertIsNotNone(fetched_t)
        assert fetched_t is not None
        self.assertEqual(fetched_t.id, r_id)

        repo.delete(r_id)
        self.assertIsNone(repo.get_by_id(r_id))


if __name__ == "__main__":
    unittest.main()
