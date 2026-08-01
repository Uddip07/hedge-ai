"""
Document Downloaders Package.
"""

from packages.rag.downloaders.base import DocumentDownloader
from packages.rag.downloaders.mock_downloader import MockDocumentDownloader

__all__ = ["DocumentDownloader", "MockDocumentDownloader"]
