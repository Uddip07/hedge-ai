"""
Mock Embedding Adapter Implementation.

Generates deterministic pseudo-random embedding vectors using text hashes for development and tests.
Zero external API dependencies.
"""

import math

from packages.rag.embeddings.base import EmbeddingPort


class MockEmbeddingAdapter(EmbeddingPort):
    """
    Mock Embedding Provider Adapter.
    """

    def __init__(self, vector_dimension: int = 128) -> None:
        self._dim = vector_dimension

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> list[float]:
        """Generate a unit-normalized deterministic vector for text based on string hashing."""
        if not text:
            return [0.0] * self._dim

        vector: list[float] = []
        seed = hash(text) & 0xFFFFFFFF
        for i in range(self._dim):
            val = math.sin(seed + i * 0.1)
            vector.append(val)

        # Normalize to unit length
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [round(x / norm, 6) for x in vector]
        return vector

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of text strings."""
        return [self.embed_text(t) for t in texts]
