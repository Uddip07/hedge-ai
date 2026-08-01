"""
Document Downloader Interface for Production RAG Ingestion Pipeline.
"""

from abc import ABC, abstractmethod

from packages.rag.models.document import Document


class DocumentDownloader(ABC):
    """
    Abstract interface for document downloaders.
    """

    @abstractmethod
    def download(self, source_url_or_path: str) -> Document:
        """
        Fetch or load document payload from remote URL or local path.

        Args:
            source_url_or_path (str): Resource URL or file path.

        Returns:
            Document: Downloaded Document object.
        """
