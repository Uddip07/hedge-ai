"""
Unit and Integration tests for Company Intelligence Engine.

Tests CompanyIntelligenceOrchestrator, CompanyIntelligenceWorkflow,
CompanyIntelligencePipeline, ResearchReportBuilder, and ResearchReport formats.
"""

import unittest
from decimal import Decimal

from packages.application.company_intelligence import (
    CompanyIntelligenceOrchestrator,
    ResearchReport,
)


class TestCompanyIntelligence(unittest.TestCase):
    def setUp(self) -> None:
        self.orchestrator = CompanyIntelligenceOrchestrator()

    def test_end_to_end_company_analysis(self) -> None:
        report = self.orchestrator.analyze_company("RELIANCE.NSE")
        self.assertIsInstance(report, ResearchReport)
        self.assertEqual(report.ticker, "RELIANCE.NSE")
        self.assertTrue(len(report.company_name) > 0)
        self.assertGreater(report.market_snapshot.price.amount, Decimal("0.00"))

        # Verify sections
        self.assertIsNotNone(report.executive_summary)
        self.assertIsNotNone(report.financial_highlights)
        self.assertIsNotNone(report.technical_analysis)
        self.assertIsNotNone(report.news_section)
        self.assertIsNotNone(report.corporate_actions)
        self.assertIsNotNone(report.macro_context)
        self.assertIsNotNone(report.agent_opinions)
        self.assertIsNotNone(report.consensus_decision)
        self.assertIsNotNone(report.explainability)

        # Verify 5 agents represented
        self.assertEqual(len(report.agent_opinions.opinions), 5)

        # Verify Source Attributions in Evidence
        self.assertGreater(len(report.explainability.evidence), 0)
        citations = report.explainability.evidence[0].citations
        self.assertGreater(len(citations), 0)
        self.assertEqual(citations[0].company, "RELIANCE Limited")

    def test_report_formats(self) -> None:
        report = self.orchestrator.analyze_company("INFY.NSE")

        # 1. JSON
        json_str = report.to_json()
        self.assertIn('"ticker": "INFY.NSE"', json_str)
        self.assertTrue(len(report.company_name) > 0)

        # 2. Dictionary
        d = report.to_dict()
        self.assertEqual(d["ticker"], "INFY.NSE")
        self.assertTrue(len(d["company_name"]) > 0)

        # 3. Markdown
        md_str = report.to_markdown()
        self.assertIn("Investment Research Report:", md_str)
        self.assertIn("## 1. Executive Summary", md_str)
        self.assertIn("## 9. Consensus Decision", md_str)

        # 4. PDF Metadata
        pdf_meta = report.to_pdf_metadata()
        self.assertEqual(pdf_meta["document_title"], "Investment Research Report - INFY.NSE")
        self.assertEqual(pdf_meta["author"], "MONEYYYYYY AI Investment Operating System")


if __name__ == "__main__":
    unittest.main()
