"""
Vector Store Port Interface for RAG Framework.

Defines outbound port contract for vector indexing, chunk storage, and similarity search.
"""

from abc import ABC, abstractmethod

from packages.rag.models.chunk import Chunk
from packages.rag.models.search import QueryResult


class VectorStorePort(ABC):
    """
    Abstract Outbound Port for Vector Database Adapters (InMemory, pgvector, Qdrant, etc.).
    """

    @abstractmethod
    def add_chunks(self, chunks: list[Chunk]) -> None:
        """
        Index and store text Chunks with embeddings.

        Args:
            chunks (list[Chunk]): List of Chunk entities with embeddings.
        """

    @abstractmethod
    def search(self, query_vector: list[float], top_k: int = 5) -> list[QueryResult]:
        """
        Execute vector similarity search for a query embedding vector.

        Args:
            query_vector (list[float]): Query dense embedding vector.
            top_k (int): Maximum number of top matching results to return.

        Returns:
            list[QueryResult]: Ranked list of QueryResult matches.
        """

    @abstractmethod
    def clear(self) -> None:
        """Clear all stored vectors and chunks."""
