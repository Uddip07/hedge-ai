"""
Base Chunker Abstraction for RAG Framework.

Defines standard interface for splitting Document content into ordered text Chunks.
"""

from abc import ABC, abstractmethod

from packages.rag.models.chunk import Chunk
from packages.rag.models.document import Document


class BaseChunker(ABC):
    """
    Abstract Base Class for text chunking algorithms.
    """

    @abstractmethod
    def chunk_document(self, document: Document) -> list[Chunk]:
        """
        Split a Document entity into a list of Chunk segments.

        Args:
            document (Document): Target Document entity.

        Returns:
            list[Chunk]: Ordered list of text Chunks.
        """
