"""
KnowledgeBase Aggregate Root for the Indian AI Hedge Fund Domain.

Root entity managing indexed financial market research documents, filings, and regulatory updates.
Pure domain entity with zero infrastructure dependencies.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any

from packages.domain.enums.research import DocumentType
from packages.domain.exceptions import EntityNotFoundError, ValidationError
from packages.domain.knowledge.documents import ResearchDocument
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import DocumentId
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass
class KnowledgeBase:
    """
    KnowledgeBase Aggregate Root.

    Attributes:
        id (uuid.UUID): Unique knowledge base repository identifier.
        name (str): Knowledge base repository name.
        documents (Dict[str, ResearchDocument]): Tracked documents map keyed by DocumentId string.
        created_at (Timestamp): Creation timestamp (UTC).
        updated_at (Timestamp): Last update timestamp (UTC).
    """

    name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    documents: dict[str, ResearchDocument] = field(default_factory=dict)
    created_at: Timestamp = field(default_factory=Timestamp.now_utc)
    updated_at: Timestamp = field(default_factory=Timestamp.now_utc)

    def __post_init__(self) -> None:
        if not isinstance(self.created_at, Timestamp):
            object.__setattr__(self, "created_at", Timestamp(self.created_at))
        if not isinstance(self.updated_at, Timestamp):
            object.__setattr__(self, "updated_at", Timestamp(self.updated_at))

        if not self.name.strip():
            raise ValidationError("KnowledgeBase name cannot be empty.")

    def add_document(self, document: ResearchDocument) -> None:
        """Add or update a research document in the knowledge base."""
        doc_key = str(document.id)
        self.documents[doc_key] = document
        self._touch()

    def remove_document(self, document_id: DocumentId) -> None:
        """
        Remove a document by ID.

        Raises:
            EntityNotFoundError: If document ID is not present.
        """
        doc_key = str(document_id)
        if doc_key not in self.documents:
            raise EntityNotFoundError(
                f"Document '{document_id}' not found in KnowledgeBase '{self.name}'.",
                context={"knowledge_base": self.name, "document_id": str(document_id)},
            )

        del self.documents[doc_key]
        self._touch()

    def search_by_ticker(self, ticker: Ticker) -> list[ResearchDocument]:
        """Return all documents associated with a given Ticker."""
        symbol = ticker.full_symbol
        return [
            doc
            for doc in self.documents.values()
            if doc.ticker and doc.ticker.full_symbol == symbol
        ]

    def filter_by_type(self, doc_type: DocumentType) -> list[ResearchDocument]:
        """Return all documents matching a specific DocumentType."""
        return [doc for doc in self.documents.values() if doc.doc_type == doc_type]

    def get_regulatory_documents(self) -> list[ResearchDocument]:
        """Return all official SEBI, RBI, or government regulatory documents."""
        return [doc for doc in self.documents.values() if doc.is_regulatory()]

    def _touch(self) -> None:
        self.updated_at = Timestamp.now_utc()

    def to_dict(self) -> dict[str, Any]:
        """Serialize KnowledgeBase Aggregate Root to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "documents": {k: v.to_dict() for k, v in self.documents.items()},
            "created_at": self.created_at.to_dict(),
            "updated_at": self.updated_at.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KnowledgeBase":
        """Deserialize dictionary to KnowledgeBase Aggregate Root."""
        documents = {k: ResearchDocument.from_dict(v) for k, v in data.get("documents", {}).items()}

        return cls(
            id=uuid.UUID(data["id"]),
            name=data["name"],
            documents=documents,
            created_at=Timestamp.from_dict(data["created_at"]),
            updated_at=Timestamp.from_dict(data["updated_at"]),
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, KnowledgeBase):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)
