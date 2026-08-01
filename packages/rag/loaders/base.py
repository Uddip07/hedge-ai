"""
Base Document Loader Abstraction for RAG Framework.

Defines standard interface for reading and constructing Document instances from file or stream sources.
"""

from abc import ABC, abstractmethod

from packages.rag.models.document import Document


class BaseDocumentLoader(ABC):
    """
    Abstract Base Class for Document Loaders (PDF, HTML, Text, SEBI filings, etc.).
    """

    @abstractmethod
    def load(self, source: str) -> list[Document]:
        """
        Load documents from a file path or URI source.

        Args:
            source (str): Source path or location string.

        Returns:
            list[Document]: Loaded document entities.
        """
