"""
Chunk Data Models for RAG Framework.

Defines ChunkMetadata and Chunk text segment models.
"""

from dataclasses import dataclass, field
from typing import Any

from packages.domain.value_objects.identifiers.uuid_wrappers import DocumentId


@dataclass(frozen=True)
class ChunkMetadata:
    """
    Metadata associated with a text Chunk segment.

    Attributes:
        chunk_id (str): Unique chunk identifier string.
        document_id (DocumentId): ID of parent Document.
        chunk_index (int): Sequence index within parent document.
        start_char (int): Starting character offset in parent text.
        end_char (int): Ending character offset in parent text.
        token_count (int): Token count estimate.
        company (str): Company name (e.g. Reliance Industries Ltd).
        ticker (str): Stock ticker symbol (e.g. RELIANCE.NS).
        filing_type (str): Filing classification (ANNUAL_REPORT, QUARTERLY_RESULTS, etc.).
        section (str): Report section name (e.g. Financial Results, MD&A).
        page (int): Source document page number.
        publication_date (str): ISO publication or filing date.
        custom_metadata (dict[str, Any]): Additional metadata attributes.
    """

    chunk_id: str
    document_id: DocumentId
    chunk_index: int
    start_char: int
    end_char: int
    token_count: int = 0
    company: str = "Unknown"
    ticker: str = "N/A"
    filing_type: str = "CORPORATE_ANNOUNCEMENT"
    section: str = "General"
    page: int = 1
    publication_date: str = ""
    custom_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize ChunkMetadata to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id.to_dict(),
            "chunk_index": self.chunk_index,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "token_count": self.token_count,
            "company": self.company,
            "ticker": self.ticker,
            "filing_type": self.filing_type,
            "section": self.section,
            "page": self.page,
            "publication_date": self.publication_date,
            "custom_metadata": dict(self.custom_metadata),
        }


@dataclass
class Chunk:
    """
    Text segment chunk entity model.

    Attributes:
        chunk_id (str): Unique chunk identifier.
        document_id (DocumentId): ID of parent Document.
        text (str): Extracted text segment.
        metadata (ChunkMetadata): Associated chunk metadata.
        embedding (list[float] | None): Dense vector representation.
    """

    chunk_id: str
    document_id: DocumentId
    text: str
    metadata: ChunkMetadata
    embedding: list[float] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize Chunk to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id.to_dict(),
            "text": self.text,
            "metadata": self.metadata.to_dict(),
            "has_embedding": self.embedding is not None,
            "embedding_dim": len(self.embedding) if self.embedding else 0,
        }
