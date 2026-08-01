"""
Unit tests verifying abstract repository interfaces contract constraints.
"""

import unittest

from packages.domain.enums.portfolio import PortfolioType
from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.repositories import (
    AssetRepository,
    BacktestRepository,
    BrokerAccountRepository,
    CompanyRepository,
    KnowledgeBaseRepository,
    PortfolioRepository,
    PromptRepository,
    ResearchReportRepository,
    StrategyRepository,
)
from packages.domain.value_objects.identifiers import PortfolioId


class DummyPortfolioRepository(PortfolioRepository):
    """InMemory test implementation of PortfolioRepository for contract verification."""

    def __init__(self) -> None:
        self._store: dict[str, Portfolio] = {}

    def get_by_id(self, portfolio_id: PortfolioId) -> Portfolio | None:
        return self._store.get(str(portfolio_id))

    def list_all(self) -> list[Portfolio]:
        return list(self._store.values())

    def save(self, portfolio: Portfolio) -> None:
        self._store[str(portfolio.id)] = portfolio

    def delete(self, portfolio_id: PortfolioId) -> None:
        self._store.pop(str(portfolio_id), None)


class TestRepositoryInterfaces(unittest.TestCase):
    """Test suite for repository interfaces."""

    def test_abstract_repository_cannot_be_instantiated(self):
        abstract_repos: list[type] = [
            PortfolioRepository,
            CompanyRepository,
            AssetRepository,
            BrokerAccountRepository,
            StrategyRepository,
            ResearchReportRepository,
            KnowledgeBaseRepository,
            BacktestRepository,
            PromptRepository,
        ]
        for repo_cls in abstract_repos:
            with self.subTest(repo=repo_cls.__name__):
                with self.assertRaises(TypeError):
                    repo_cls()

    def test_dummy_repository_implementation(self):
        repo = DummyPortfolioRepository()
        port = Portfolio(name="Test Portfolio", portfolio_type=PortfolioType.PAPER)

        repo.save(port)
        self.assertEqual(len(repo.list_all()), 1)

        fetched = repo.get_by_id(port.id)
        self.assertIsNotNone(fetched)
        assert fetched is not None
        self.assertEqual(fetched.name, "Test Portfolio")

        repo.delete(port.id)
        self.assertIsNone(repo.get_by_id(port.id))


if __name__ == "__main__":
    unittest.main()
