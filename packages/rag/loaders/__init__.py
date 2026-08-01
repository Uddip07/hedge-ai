"""
RAG Loaders Package.

Exports BaseDocumentLoader and MockPDFLoader.
"""

from packages.rag.loaders.base import BaseDocumentLoader
from packages.rag.loaders.mock_pdf_loader import MockPDFLoader

__all__ = ["BaseDocumentLoader", "MockPDFLoader"]
