"""
Embedding Port Interface for RAG Framework.

Defines outbound port contract for text embedding vector generation.
"""

from abc import ABC, abstractmethod


class EmbeddingPort(ABC):
    """
    Abstract Outbound Port for Text Embedding Provider Adapters.
    """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return vector dimension size (e.g. 128, 768, 1536)."""

    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding vector for a single text string.

        Args:
            text (str): Input text string.

        Returns:
            list[float]: Floating-point dense vector.
        """

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embedding vectors for a batch of text strings.

        Args:
            texts (list[str]): List of text strings.

        Returns:
            list[list[float]]: List of dense vectors.
        """
