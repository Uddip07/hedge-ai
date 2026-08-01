"""
Unit tests for Research Domain Enums.
"""

import unittest

from packages.domain.enums.research import (
    DocumentType,
    RecommendationType,
    ResearchStatus,
)


class TestResearchEnums(unittest.TestCase):
    """Test suite for Research Enums."""

    def test_research_status_helpers(self):
        self.assertTrue(ResearchStatus.COMPLETED.is_final())
        self.assertTrue(ResearchStatus.APPROVED.is_actionable())
        self.assertFalse(ResearchStatus.DRAFT.is_final())

    def test_recommendation_type_helpers(self):
        self.assertEqual(RecommendationType.STRONG_BUY.score(), 2)
        self.assertEqual(RecommendationType.STRONG_SELL.score(), -2)
        self.assertTrue(RecommendationType.BUY.is_bullish())
        self.assertTrue(RecommendationType.SELL.is_bearish())

    def test_document_type_helpers(self):
        self.assertTrue(DocumentType.SEBI_CIRCULAR.is_regulatory())
        self.assertTrue(DocumentType.ANNUAL_REPORT.is_financial_statement())


if __name__ == "__main__":
    unittest.main()
