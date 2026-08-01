"""
Unit tests for AnalyzeStockUseCase, AnalyzeStockCommand, AnalyzeStockResultDTO,
StockAnalysisMapper, and ResearchApplicationService.
"""

import unittest
import uuid
from decimal import Decimal

from packages.application.commands import AnalyzeStockCommand
from packages.application.dto import AnalyzeStockResultDTO
from packages.application.exceptions import ValidationApplicationError
from packages.application.mappers import StockAnalysisMapper
from packages.application.ports import PortfolioPort, ResearchPort
from packages.application.services import ResearchApplicationService
from packages.application.use_cases import AnalyzeStockUseCase
from packages.domain.enums.portfolio import PortfolioType
from packages.domain.enums.research import RecommendationType
from packages.domain.enums.risk import RiskLevel
from packages.domain.portfolio.portfolio import Portfolio
from packages.domain.portfolio.snapshot import PortfolioSnapshot
from packages.domain.research.consensus import ConsensusDecision
from packages.domain.research.report import ResearchReport
from packages.domain.value_objects.core.money import Money
from packages.domain.value_objects.identifiers import PortfolioId, Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import ResearchId
from packages.domain.value_objects.metrics.scores import RecommendationScore
from packages.domain.value_objects.temporal.timestamps import Timestamp


class MockResearchPort(ResearchPort):
    def __init__(self) -> None:
        self.scores: dict[str, RecommendationScore] = {}

    def get_latest_recommendation_score(self, ticker: Ticker) -> RecommendationScore | None:
        return self.scores.get(ticker.full_symbol)

    def get_research_report(self, report_id: ResearchId) -> ResearchReport | None:
        return None

    def save_research_report(self, report: ResearchReport) -> None:
        pass

    def get_consensus_decision(self, report_id: ResearchId) -> ConsensusDecision | None:
        return None


class MockPortfolioPort(PortfolioPort):
    def __init__(self) -> None:
        self.portfolios: dict[str, Portfolio] = {}

    def get_portfolio_by_id(self, portfolio_id: PortfolioId) -> Portfolio | None:
        return self.portfolios.get(str(portfolio_id.value))

    def save_portfolio(self, portfolio: Portfolio) -> None:
        self.portfolios[str(portfolio.id.value)] = portfolio

    def get_portfolio_snapshots(self, portfolio_id: PortfolioId) -> list[PortfolioSnapshot]:
        return []


class TestAnalyzeStockUseCase(unittest.TestCase):
    def setUp(self) -> None:
        self.research_port = MockResearchPort()
        self.portfolio_port = MockPortfolioPort()
        self.mapper = StockAnalysisMapper()
        self.use_case = AnalyzeStockUseCase(
            research_port=self.research_port,
            portfolio_port=self.portfolio_port,
            mapper=self.mapper,
        )
        self.service = ResearchApplicationService(self.use_case)

    def test_analyze_stock_command_validations(self) -> None:
        cmd = AnalyzeStockCommand(ticker_symbol="RELIANCE.NSE")
        self.assertEqual(cmd.ticker_symbol, "RELIANCE.NSE")
        self.assertEqual(cmd.investment_horizon_days, 365)
        self.assertIsNone(cmd.portfolio_id)

        with self.assertRaises(ValidationApplicationError):
            AnalyzeStockCommand(ticker_symbol="")

        with self.assertRaises(ValidationApplicationError):
            AnalyzeStockCommand(ticker_symbol="RELIANCE.NSE", investment_horizon_days=-10)

    def test_analyze_stock_dto_serialization(self) -> None:
        dto = AnalyzeStockResultDTO(
            ticker="TCS.NSE",
            recommendation="BUY",
            consensus_score=0.85,
            risk_level="LOW",
            is_suitable_for_portfolio=True,
            reasoning_summary="Strong fundamentals and momentum.",
            analyzed_at=Timestamp.now_utc().isoformat(),
        )

        d = dto.to_dict()
        self.assertEqual(d["ticker"], "TCS.NSE")
        self.assertEqual(d["recommendation"], "BUY")
        self.assertEqual(d["consensus_score"], 0.85)

        restored = AnalyzeStockResultDTO.from_dict(d)
        self.assertEqual(restored, dto)

    def test_stock_analysis_mapper_conversions(self) -> None:
        ticker = Ticker("INFY.NSE")
        score = RecommendationScore(Decimal("0.82"))
        domain_dict = {
            "ticker": ticker,
            "recommendation": RecommendationType.STRONG_BUY,
            "consensus_score": score,
            "risk_level": RiskLevel.LOW,
            "is_suitable": True,
            "reasoning_summary": "High consensus score.",
            "timestamp": Timestamp.now_utc(),
        }

        dto = self.mapper.to_dto(domain_dict)
        self.assertEqual(dto.ticker, "INFY.NSE")
        self.assertEqual(dto.recommendation, "STRONG_BUY")
        self.assertEqual(dto.consensus_score, 0.82)
        self.assertEqual(dto.risk_level, "LOW")

        restored = self.mapper.to_domain(dto)
        self.assertEqual(restored["ticker"], ticker)
        self.assertEqual(restored["recommendation"], RecommendationType.STRONG_BUY)

    def test_use_case_execution_without_portfolio(self) -> None:
        cmd = AnalyzeStockCommand(ticker_symbol="RELIANCE.NSE")
        result = self.use_case.execute(cmd)

        self.assertIsInstance(result, AnalyzeStockResultDTO)
        self.assertEqual(result.ticker, "RELIANCE.NSE")
        # When no research score exists, the use case applies a neutral HOLD baseline
        # at 0.50 rather than fabricating a bullish BUY at 0.75.
        self.assertEqual(result.recommendation, "HOLD")
        self.assertEqual(result.consensus_score, 0.50)
        self.assertEqual(result.risk_level, "MEDIUM")
        self.assertTrue(result.is_suitable_for_portfolio)

    def test_use_case_execution_with_existing_score(self) -> None:
        t = Ticker("HDFCBANK.NSE")
        self.research_port.scores[t.full_symbol] = RecommendationScore(Decimal("0.45"))

        cmd = AnalyzeStockCommand(ticker_symbol="HDFCBANK.NSE")
        result = self.use_case.execute(cmd)

        self.assertEqual(result.ticker, "HDFCBANK.NSE")
        self.assertEqual(result.recommendation, "HOLD")
        self.assertEqual(result.consensus_score, 0.45)
        self.assertEqual(result.risk_level, "MEDIUM")

    def test_use_case_execution_with_portfolio_suitability(self) -> None:
        p_id = PortfolioId.generate()
        portfolio = Portfolio(
            id=p_id,
            name="Test Portfolio",
            portfolio_type=PortfolioType.PAPER,
            cash_balance=Money(Decimal("10000.00")),
        )
        self.portfolio_port.save_portfolio(portfolio)

        cmd = AnalyzeStockCommand(
            ticker_symbol="ICICIBANK.NSE",
            portfolio_id=p_id.value,
        )
        result = self.use_case.execute(cmd)

        self.assertEqual(result.ticker, "ICICIBANK.NSE")
        self.assertTrue(result.is_suitable_for_portfolio)

    def test_use_case_invalid_ticker_throws_validation_error(self) -> None:
        cmd = AnalyzeStockCommand(ticker_symbol="INVALID_FORMAT")
        with self.assertRaises(ValidationApplicationError):
            self.use_case.execute(cmd)

    def test_research_application_service_orchestration(self) -> None:
        user_id = uuid.uuid4()
        result = self.service.analyze_stock(
            ticker_symbol="SBIN.NSE",
            user_id=user_id,
        )

        self.assertIsInstance(result, AnalyzeStockResultDTO)
        self.assertEqual(result.ticker, "SBIN.NSE")
        # No research score in MockResearchPort → neutral HOLD baseline
        self.assertEqual(result.recommendation, "HOLD")


if __name__ == "__main__":
    unittest.main()
