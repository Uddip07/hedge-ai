"""
Exceptions for Company Intelligence Application Context.

Defines domain exceptions for orchestration, pipeline execution, document retrieval,
and research report generation.
"""

from typing import Any


class CompanyIntelligenceError(Exception):
    """
    Base Exception for all Company Intelligence application errors.

    Attributes:
        message (str): Explanatory error message.
        details (dict[str, Any]): Contextual error metadata.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class PipelineExecutionError(CompanyIntelligenceError):
    """Raised when a stage in the company intelligence pipeline fails."""


class DocumentRetrievalError(CompanyIntelligenceError):
    """Raised when RAG document discovery or retrieval fails."""


class ReportGenerationError(CompanyIntelligenceError):
    """Raised when structured research report generation or formatting fails."""
