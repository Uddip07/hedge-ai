"""
Storage Manager for Production RAG Ingestion Pipeline.

Persists raw document text, extracted sections/tables, and chunk embeddings.
"""

from typing import Any

from packages.domain.value_objects.identifiers.uuid_wrappers import DocumentId
from packages.rag.models.chunk import Chunk
from packages.rag.models.document import Document


class StorageManager:
    """
    Manager persisting documents and processed chunks.
    """

    def __init__(self) -> None:
        self._documents: dict[DocumentId, Document] = {}
        self._chunks: dict[str, Chunk] = {}
        self._extractions: dict[DocumentId, dict[str, Any]] = {}

    def save_document(self, document: Document, extractions: dict[str, Any] | None = None) -> None:
        """Persist Document entity and extracted sections/tables metadata."""
        self._documents[document.id] = document
        if extractions:
            self._extractions[document.id] = extractions

    def save_chunks(self, chunks: list[Chunk]) -> None:
        """Persist processed Chunk entities."""
        for c in chunks:
            self._chunks[c.chunk_id] = c

    def get_document(self, document_id: DocumentId) -> Document | None:
        """Fetch stored Document by DocumentId."""
        return self._documents.get(document_id)

    def get_chunks_for_document(self, document_id: DocumentId) -> list[Chunk]:
        """Fetch all chunks associated with a target DocumentId."""
        return [c for c in self._chunks.values() if c.document_id == document_id]

    def list_documents(self) -> list[Document]:
        """List all stored documents."""
        return list(self._documents.values())

    def clear(self) -> None:
        """Clear all stored documents and chunks."""
        self._documents.clear()
        self._chunks.clear()
        self._extractions.clear()
