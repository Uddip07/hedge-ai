"""
Document Manager for RAG Framework.

In-memory document repository for registering, fetching, and removing Document instances.
"""

from packages.domain.value_objects.identifiers.uuid_wrappers import DocumentId
from packages.rag.exceptions.exceptions import DocumentLoadingError
from packages.rag.models.document import Document


class DocumentManager:
    """
    In-memory manager tracking ingested documents.
    """

    def __init__(self) -> None:
        self._documents: dict[str, Document] = {}

    def add_document(self, document: Document) -> None:
        """Register a Document in the manager."""
        self._documents[str(document.id.value)] = document

    def get_document(self, document_id: DocumentId | str) -> Document:
        """Fetch a registered Document by ID."""
        key = str(document_id.value) if isinstance(document_id, DocumentId) else document_id
        if key not in self._documents:
            raise DocumentLoadingError(f"Document with ID '{key}' not found in DocumentManager.")
        return self._documents[key]

    def list_documents(self) -> list[Document]:
        """List all stored Document entities."""
        return list(self._documents.values())

    def remove_document(self, document_id: DocumentId | str) -> None:
        """Remove a Document from the manager."""
        key = str(document_id.value) if isinstance(document_id, DocumentId) else document_id
        self._documents.pop(key, None)

    def clear(self) -> None:
        """Clear all stored documents."""
        self._documents.clear()
