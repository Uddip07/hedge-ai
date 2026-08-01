"""
RAG Exceptions for Infrastructure & Framework Layer.

Defines exception hierarchy for document loading, parsing, chunking, embedding,
vector storage, and retrieval operations.
"""

from typing import Any


class RAGException(Exception):
    """Base exception for all RAG framework operations."""

    def __init__(
        self,
        message: str,
        code: str = "RAG_ERROR",
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.context = context or {}


class DocumentLoadingError(RAGException):
    """Raised when loading a document from disk or source fails."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="DOCUMENT_LOADING_ERROR", context=context)


class DocumentParsingError(RAGException):
    """Raised when parsing document raw content into plain text fails."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="DOCUMENT_PARSING_ERROR", context=context)


class ChunkingError(RAGException):
    """Raised when splitting document text into chunks fails."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="CHUNKING_ERROR", context=context)


class EmbeddingError(RAGException):
    """Raised when generating embedding vectors fails."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="EMBEDDING_ERROR", context=context)


class VectorStoreError(RAGException):
    """Raised when vector database indexing or search fails."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="VECTOR_STORE_ERROR", context=context)


class RetrievalError(RAGException):
    """Raised when vector or hybrid document retrieval fails."""

    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="RETRIEVAL_ERROR", context=context)
