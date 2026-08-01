"""
Research & Knowledge Enums for the Indian AI Hedge Fund Domain.

Defines research workflow status, analyst recommendations, and knowledge base
document types (including Indian regulatory sources like SEBI and RBI).
"""

from enum import StrEnum


class ResearchStatus(StrEnum):
    """
    Lifecycle status of a research thesis or multi-agent research task.
    """

    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"

    def is_final(self) -> bool:
        """Return True if research analysis is finished."""
        return self in {
            ResearchStatus.COMPLETED,
            ResearchStatus.APPROVED,
            ResearchStatus.REJECTED,
            ResearchStatus.ARCHIVED,
        }

    def is_actionable(self) -> bool:
        """Return True if research has been completed and approved for strategy execution."""
        return self in {ResearchStatus.COMPLETED, ResearchStatus.APPROVED}


class RecommendationType(StrEnum):
    """
    Investment recommendation classification.
    """

    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"

    def score(self) -> int:
        """
        Return a numeric rating from +2 (Strong Buy) to -2 (Strong Sell).
        """
        scores = {
            RecommendationType.STRONG_BUY: 2,
            RecommendationType.BUY: 1,
            RecommendationType.HOLD: 0,
            RecommendationType.SELL: -1,
            RecommendationType.STRONG_SELL: -2,
        }
        return scores[self]

    def is_bullish(self) -> bool:
        """Return True if the recommendation is positive."""
        return self in {RecommendationType.STRONG_BUY, RecommendationType.BUY}

    def is_bearish(self) -> bool:
        """Return True if the recommendation is negative."""
        return self in {RecommendationType.SELL, RecommendationType.STRONG_SELL}


class DocumentType(StrEnum):
    """
    Knowledge base document types for Indian financial market analysis.
    """

    ANNUAL_REPORT = "ANNUAL_REPORT"
    QUARTERLY_REPORT = "QUARTERLY_REPORT"
    SEBI_CIRCULAR = "SEBI_CIRCULAR"
    RBI_REPORT = "RBI_REPORT"
    BUDGET_DOCUMENT = "BUDGET_DOCUMENT"
    NEWS_ARTICLE = "NEWS_ARTICLE"
    TRANSCRIPT = "TRANSCRIPT"
    RESEARCH_NOTE = "RESEARCH_NOTE"
    CREDIT_RATING_REPORT = "CREDIT_RATING_REPORT"

    def is_regulatory(self) -> bool:
        """Return True if the document originates from an official regulator (SEBI, RBI)."""
        return self in {
            DocumentType.SEBI_CIRCULAR,
            DocumentType.RBI_REPORT,
            DocumentType.BUDGET_DOCUMENT,
        }

    def is_financial_statement(self) -> bool:
        """Return True if the document contains company corporate filings."""
        return self in {DocumentType.ANNUAL_REPORT, DocumentType.QUARTERLY_REPORT}
