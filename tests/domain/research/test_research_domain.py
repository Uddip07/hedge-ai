"""
Unit tests for ResearchReport Aggregate Root and child research models (Analyses, Agent Consensus, Recommendations).
"""

import unittest
from decimal import Decimal

from packages.domain.enums.ai import AgentType
from packages.domain.enums.research import RecommendationType, ResearchStatus
from packages.domain.enums.strategy import SignalType
from packages.domain.research import (
    AgentOpinion,
    FinalRecommendation,
    FundamentalAnalysis,
    MacroAnalysis,
    ResearchReport,
    SentimentAnalysis,
    TechnicalAnalysis,
)
from packages.domain.value_objects.core import Percentage
from packages.domain.value_objects.identifiers import Ticker
from packages.domain.value_objects.metrics import (
    RSI,
    ConfidenceScore,
    RecommendationScore,
)


class TestResearchDomain(unittest.TestCase):
    """Test suite for ResearchReport Aggregate Root and research models."""

    def test_analysis_models_serialization(self):
        fund = FundamentalAnalysis(
            pe_ratio=Decimal("22.5"),
            pb_ratio=Decimal("3.1"),
            roe_pct=Percentage(Decimal("18.5")),
            summary="Strong ROE and healthy balance sheet.",
        )
        fund_dict = fund.to_dict()
        restored_fund = FundamentalAnalysis.from_dict(fund_dict)
        self.assertEqual(restored_fund.pe_ratio, Decimal("22.5"))
        assert restored_fund.roe_pct is not None
        self.assertEqual(restored_fund.roe_pct.value, Decimal("18.5"))

        tech = TechnicalAnalysis(
            rsi=RSI(Decimal("62.5")),
            trend_signal=SignalType.BUY,
            summary="Bullish momentum above 50-day EMA.",
        )
        assert tech.rsi is not None
        self.assertEqual(tech.rsi.value, Decimal("62.5"))
        self.assertEqual(tech.trend_signal, SignalType.BUY)

    def test_agent_opinion_and_consensus_calculation(self):
        op_quant = AgentOpinion(
            agent_type=AgentType.QUANT,
            recommendation=RecommendationType.BUY,
            reasoning="Positive momentum factor rank.",
            confidence=ConfidenceScore(Decimal("0.85")),
        )
        op_fund = AgentOpinion(
            agent_type=AgentType.FUNDAMENTAL,
            recommendation=RecommendationType.STRONG_BUY,
            reasoning="Undervalued relative to peers.",
            confidence=ConfidenceScore(Decimal("0.90")),
        )

        t = Ticker("RELIANCE.NSE")
        report = ResearchReport(ticker=t)
        self.assertEqual(report.status, ResearchStatus.DRAFT)

        # Finalize consensus
        consensus = report.finalize_consensus([op_quant, op_fund])
        self.assertEqual(report.status, ResearchStatus.COMPLETED)
        self.assertIsNotNone(report.consensus)
        self.assertGreater(consensus.consensus_score.value, Decimal("0.0"))

    def test_research_report_approval_workflow(self):
        t = Ticker("TCS.NSE")
        report = ResearchReport(ticker=t)

        report.update_fundamental(FundamentalAnalysis(pe_ratio=Decimal("28.0")))
        report.update_technical(TechnicalAnalysis(trend_signal=SignalType.BUY))
        report.update_macro(MacroAnalysis(rbi_policy_stance="NEUTRAL"))
        report.update_sentiment(SentimentAnalysis(sebi_filing_sentiment="POSITIVE"))

        final_rec = FinalRecommendation(
            recommendation=RecommendationType.BUY,
            score=RecommendationScore(Decimal("0.75")),
            confidence=ConfidenceScore(Decimal("0.88")),
            rationale="Approved for model portfolio inclusion.",
        )

        report.approve_report(final_rec)
        self.assertEqual(report.status, ResearchStatus.APPROVED)
        assert report.final_recommendation is not None
        self.assertEqual(report.final_recommendation.recommendation, RecommendationType.BUY)

        # Verify full dict roundtrip
        dict_data = report.to_dict()
        restored = ResearchReport.from_dict(dict_data)
        self.assertEqual(restored.ticker.full_symbol, "TCS.NSE")
        self.assertEqual(restored.status, ResearchStatus.APPROVED)
        assert restored.final_recommendation is not None
        self.assertEqual(restored.final_recommendation.recommendation, RecommendationType.BUY)


if __name__ == "__main__":
    unittest.main()
