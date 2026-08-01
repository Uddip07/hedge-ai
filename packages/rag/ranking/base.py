"""
Base Ranking / Reranker Abstraction for RAG Framework.

Defines standard interface for post-retrieval reranking of search results.
"""

from abc import ABC, abstractmethod

from packages.rag.models.search import QueryResult


class BaseReranker(ABC):
    """
    Abstract Base Class for post-retrieval result rerankers (Cross-Encoder, Cohere, BM25-boost, etc.).
    """

    @abstractmethod
    def rerank(self, query: str, results: list[QueryResult]) -> list[QueryResult]:
        """
        Rerank and re-order query results according to refined relevance criteria.

        Args:
            query (str): Input query text.
            results (list[QueryResult]): Initial candidate search matches.

        Returns:
            list[QueryResult]: Reranked QueryResult list.
        """
