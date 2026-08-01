"""
RAG Embeddings Package.

Exports EmbeddingPort and MockEmbeddingAdapter.
"""

from packages.rag.embeddings.base import EmbeddingPort
from packages.rag.embeddings.mock_embedding_adapter import MockEmbeddingAdapter

__all__ = ["EmbeddingPort", "MockEmbeddingAdapter"]
