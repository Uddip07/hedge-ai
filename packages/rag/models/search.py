"""
Search & Retrieval Models for RAG Framework.

Defines QueryResult capturing matched Chunk, similarity score, and ranking order.
"""

from dataclasses import dataclass
from typing import Any

from packages.rag.models.chunk import Chunk


@dataclass(frozen=True)
class QueryResult:
    """
    Search match result model returned by retriever and reranker components.

    Attributes:
        chunk (Chunk): Matched text Chunk.
        score (float): Similarity or relevance score [0.0, 1.0].
        rank (int): Rank ordering position (1-based).
    """

    chunk: Chunk
    score: float
    rank: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Serialize QueryResult to dictionary."""
        return {
            "chunk": self.chunk.to_dict(),
            "score": round(self.score, 4),
            "rank": self.rank,
        }
