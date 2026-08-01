"""
Unit tests for KnowledgeBase Aggregate Root and specialized research document models.
"""

import unittest

from packages.domain.enums.research import DocumentType
from packages.domain.exceptions import EntityNotFoundError
from packages.domain.knowledge import (
    KnowledgeBase,
    RBIReport,
    ResearchDocument,
    SEBICircular,
)
from packages.domain.value_objects.identifiers import DocumentId, Ticker
from packages.domain.value_objects.temporal import Timestamp


class TestKnowledgeDomain(unittest.TestCase):
    """Test suite for KnowledgeBase Aggregate Root and research document models."""

    def test_research_document_word_count_and_serialization(self):
        t = Ticker("RELIANCE.NSE")
        doc = ResearchDocument(
            title="Reliance Q1 Earnings Analysis",
            doc_type=DocumentType.QUARTERLY_REPORT,
            content="Strong performance driven by retail and digital services segments.",
            published_at=Timestamp.now_utc(),
            ticker=t,
        )

        self.assertGreater(doc.word_count, 0)
        self.assertFalse(doc.is_regulatory())

        doc_dict = doc.to_dict()
        restored = ResearchDocument.from_dict(doc_dict)
        self.assertEqual(restored.title, doc.title)
        assert restored.ticker is not None
        self.assertEqual(restored.ticker.full_symbol, "RELIANCE.NSE")

    def test_specialized_documents(self):
        sebi = SEBICircular(
            title="SEBI Circular on Algo Trading Regulations",
            content="Mandatory risk checks for quantitative trading strategies.",
            published_at=Timestamp.now_utc(),
            circular_number="SEBI/HO/MIRSD/2026/01",
        )
        self.assertEqual(sebi.doc_type, DocumentType.SEBI_CIRCULAR)
        self.assertTrue(sebi.is_regulatory())

        rbi = RBIReport(
            title="RBI Monetary Policy Committee Resolution",
            content="MPC decides to keep Repo Rate unchanged.",
            published_at=Timestamp.now_utc(),
        )
        self.assertEqual(rbi.doc_type, DocumentType.RBI_REPORT)
        self.assertTrue(rbi.is_regulatory())

    def test_knowledge_base_aggregate_workflow(self):
        kb = KnowledgeBase(name="Indian AI Hedge Fund Knowledge Repository")
        t_rel = Ticker("RELIANCE.NSE")
        t_infy = Ticker("INFY.NSE")

        doc1 = ResearchDocument(
            title="Reliance Annual Report FY26",
            doc_type=DocumentType.ANNUAL_REPORT,
            content="Annual balance sheet and cash flow statement.",
            published_at=Timestamp.now_utc(),
            ticker=t_rel,
        )

        sebi_doc = SEBICircular(
            title="SEBI Master Circular for Mutual Funds",
            content="Updated NAV calculation guidelines.",
            published_at=Timestamp.now_utc(),
        )

        # Add documents
        kb.add_document(doc1)
        kb.add_document(sebi_doc)

        self.assertEqual(len(kb.documents), 2)

        # Search by ticker
        rel_docs = kb.search_by_ticker(t_rel)
        self.assertEqual(len(rel_docs), 1)
        self.assertEqual(rel_docs[0].title, doc1.title)

        # Filter by regulatory type
        reg_docs = kb.get_regulatory_documents()
        self.assertEqual(len(reg_docs), 1)
        self.assertEqual(reg_docs[0].doc_type, DocumentType.SEBI_CIRCULAR)

        # Remove document
        kb.remove_document(doc1.id)
        self.assertEqual(len(kb.documents), 1)

        with self.assertRaises(EntityNotFoundError):
            kb.remove_document(DocumentId.generate())


if __name__ == "__main__":
    unittest.main()
