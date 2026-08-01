"""
In-Memory Vector Store Adapter Implementation.

Stores chunks and vectors in memory and performs exact cosine similarity search.
Zero external vector database dependencies (No Pinecone, Chroma, pgvector, or Qdrant).
"""

import math

from packages.rag.models.chunk import Chunk
from packages.rag.models.search import QueryResult
from packages.rag.vector_store.base import VectorStorePort


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Calculate cosine similarity between two float vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b, strict=False))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(dot / (norm_a * norm_b))


class InMemoryVectorStoreAdapter(VectorStorePort):
    """
    In-Memory Vector Store Adapter implementing VectorStorePort.
    """

    def __init__(self) -> None:
        self._chunks: dict[str, Chunk] = {}

    def add_chunks(self, chunks: list[Chunk]) -> None:
        """Add or update chunks in the in-memory index."""
        for chunk in chunks:
            self._chunks[chunk.chunk_id] = chunk

    def search(self, query_vector: list[float], top_k: int = 5) -> list[QueryResult]:
        """Perform exact cosine similarity search against stored chunks."""
        if not self._chunks or not query_vector:
            return []

        matches: list[tuple[Chunk, float]] = []

        for chunk in self._chunks.values():
            if chunk.embedding is not None:
                score = _cosine_similarity(query_vector, chunk.embedding)
            else:
                score = 0.0
            matches.append((chunk, score))

        # Sort descending by similarity score
        matches.sort(key=lambda item: item[1], reverse=True)

        results: list[QueryResult] = []
        for rank, (chunk, score) in enumerate(matches[:top_k], start=1):
            results.append(QueryResult(chunk=chunk, score=score, rank=rank))

        return results

    def clear(self) -> None:
        """Clear stored chunks."""
        self._chunks.clear()
