"""
Document Data Models for RAG Framework.

Defines DocumentMetadata and Document entities wrapping domain DocumentId.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from packages.domain.value_objects.identifiers.uuid_wrappers import DocumentId


@dataclass(frozen=True)
class DocumentMetadata:
    """
    Metadata associated with a source document.

    Attributes:
        source (str): Document file path or URI origin.
        title (str): Human-readable document title.
        author (str | None): Author or publishing entity name.
        file_type (str): File extension format (pdf, html, md, txt).
        created_at (str): Document creation timestamp (ISO-8601 UTC).
        custom_metadata (dict[str, Any]): Additional key-value metadata attributes.
    """

    source: str
    title: str
    author: str | None = None
    file_type: str = "pdf"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    custom_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize DocumentMetadata to dictionary."""
        return {
            "source": self.source,
            "title": self.title,
            "author": self.author,
            "file_type": self.file_type,
            "created_at": self.created_at,
            "custom_metadata": dict(self.custom_metadata),
        }


@dataclass
class Document:
    """
    Document entity model.

    Attributes:
        id (DocumentId): Unique document identifier.
        content (str): Full raw text content of the document.
        metadata (DocumentMetadata): Associated document metadata.
    """

    content: str
    metadata: DocumentMetadata
    id: DocumentId = field(default_factory=DocumentId.generate)

    def to_dict(self) -> dict[str, Any]:
        """Serialize Document to dictionary."""
        return {
            "id": self.id.to_dict(),
            "content": self.content,
            "metadata": self.metadata.to_dict(),
        }
