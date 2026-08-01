"""
Knowledge Domain Package for the Indian AI Hedge Fund Platform.

Consolidates KnowledgeBase Aggregate Root, ResearchDocument, AnnualReport, NewsArticle,
SEBICircular, RBIReport, BudgetDocument, Transcript, ResearchNote, and PDFDocument.
"""

from packages.domain.knowledge.documents import (
    AnnualReport,
    BudgetDocument,
    NewsArticle,
    PDFDocument,
    RBIReport,
    ResearchDocument,
    ResearchNote,
    SEBICircular,
    Transcript,
)
from packages.domain.knowledge.knowledge_base import KnowledgeBase

__all__ = [
    "KnowledgeBase",
    "ResearchDocument",
    "AnnualReport",
    "NewsArticle",
    "SEBICircular",
    "RBIReport",
    "BudgetDocument",
    "Transcript",
    "ResearchNote",
    "PDFDocument",
]
