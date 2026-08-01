"""
Base Retriever Abstraction for RAG Framework.

Defines standard interface for retrieving relevant document Chunks for a user query.
"""

from abc import ABC, abstractmethod

from packages.rag.models.search import QueryResult


class BaseRetriever(ABC):
    """
    Abstract Base Class for Document Retrievers (Vector, Keyword BM25, Hybrid).
    """

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list[QueryResult]:
        """
        Retrieve relevant matched Chunks for a given query text.

        Args:
            query (str): Query string.
            top_k (int): Number of top results to retrieve.

        Returns:
            list[QueryResult]: List of ranked matching QueryResult items.
        """
