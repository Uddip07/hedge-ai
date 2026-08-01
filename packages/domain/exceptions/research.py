"""
Research & Strategy Exceptions for the Indian AI Hedge Fund Domain.

Defines errors related to quantitative strategy execution, research synthesis, and knowledge documents.
"""

from packages.domain.exceptions.base import DomainError


class ResearchError(DomainError):
    """Base exception for research orchestration failures."""

    DEFAULT_CODE = "RESEARCH_ERROR"


class StrategyError(ResearchError):
    """Raised when quantitative strategy parameter optimization or signal generation fails."""

    DEFAULT_CODE = "STRATEGY_ERROR"


class KnowledgeError(ResearchError):
    """Raised when knowledge document indexing, parsing, or retrieval fails."""

    DEFAULT_CODE = "KNOWLEDGE_ERROR"
