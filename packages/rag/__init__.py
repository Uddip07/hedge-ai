"""
Indian AI Hedge Fund - RAG Foundation & Production Document Ingestion Pipeline Package.

Provides provider-agnostic Retrieval-Augmented Generation (RAG) framework and
production document ingestion pipeline for Indian financial filings.
"""

from packages.rag.chunking import BaseChunker, FixedSizeChunker, OverlappingChunker
from packages.rag.deduplication import DeduplicationEngine
from packages.rag.documents import DocumentManager
from packages.rag.downloaders import DocumentDownloader, MockDocumentDownloader
from packages.rag.embeddings import EmbeddingPort, MockEmbeddingAdapter
from packages.rag.exceptions import (
    ChunkingError,
    DocumentLoadingError,
    DocumentParsingError,
    EmbeddingError,
    RAGException,
    RetrievalError,
    VectorStoreError,
)
from packages.rag.extractors import (
    HTMLParser,
    MarkdownParser,
    PDFParser,
    SectionExtractor,
    TableExtractor,
)
from packages.rag.ingestion import IngestionPipeline
from packages.rag.loaders import BaseDocumentLoader, MockPDFLoader
from packages.rag.metadata import MetadataBuilder
from packages.rag.models import Chunk, ChunkMetadata, Document, DocumentMetadata, QueryResult
from packages.rag.normalizers import DocumentValidator
from packages.rag.parsers import BaseDocumentParser, MockDocumentParser
from packages.rag.pipeline import DocumentPipeline
from packages.rag.ranking import BaseReranker, MockReranker
from packages.rag.retriever import BaseRetriever, VectorRetriever
from packages.rag.storage import StorageManager
from packages.rag.vector_store import InMemoryVectorStoreAdapter, VectorStorePort

__version__ = "1.0.0"

__all__ = [
    "BaseChunker",
    "BaseDocumentLoader",
    "BaseDocumentParser",
    "BaseReranker",
    "BaseRetriever",
    "Chunk",
    "ChunkMetadata",
    "ChunkingError",
    "DeduplicationEngine",
    "Document",
    "DocumentDownloader",
    "DocumentLoadingError",
    "DocumentManager",
    "DocumentMetadata",
    "DocumentParsingError",
    "DocumentPipeline",
    "DocumentValidator",
    "EmbeddingError",
    "EmbeddingPort",
    "FixedSizeChunker",
    "HTMLParser",
    "InMemoryVectorStoreAdapter",
    "IngestionPipeline",
    "MarkdownParser",
    "MetadataBuilder",
    "MockDocumentDownloader",
    "MockDocumentParser",
    "MockEmbeddingAdapter",
    "MockPDFLoader",
    "MockReranker",
    "OverlappingChunker",
    "PDFParser",
    "QueryResult",
    "RAGException",
    "RetrievalError",
    "SectionExtractor",
    "StorageManager",
    "TableExtractor",
    "VectorRetriever",
    "VectorStoreError",
    "VectorStorePort",
]
