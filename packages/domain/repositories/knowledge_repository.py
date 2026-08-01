"""
KnowledgeBase Repository Interface for the Indian AI Hedge Fund Platform.

Abstract repository specification for KnowledgeBase Aggregate Root persistence.
Pure domain interface with zero infrastructure dependencies.
"""

import uuid
from abc import ABC, abstractmethod

from packages.domain.knowledge.documents import ResearchDocument
from packages.domain.knowledge.knowledge_base import KnowledgeBase
from packages.domain.value_objects.identifiers.uuid_wrappers import DocumentId


class KnowledgeBaseRepository(ABC):
    """
    Abstract Repository Interface for KnowledgeBase Aggregate Root persistence.
    """

    @abstractmethod
    def get_by_id(self, kb_id: uuid.UUID) -> KnowledgeBase | None:
        """Fetch KnowledgeBase Aggregate Root by unique UUID identifier."""
        pass

    @abstractmethod
    def get_document_by_id(self, document_id: DocumentId) -> ResearchDocument | None:
        """Fetch individual ResearchDocument by DocumentId."""
        pass

    @abstractmethod
    def list_all(self) -> list[KnowledgeBase]:
        """List all knowledge bases."""
        pass

    @abstractmethod
    def save(self, kb: KnowledgeBase) -> None:
        """Persist or update a KnowledgeBase Aggregate Root."""
        pass

    @abstractmethod
    def delete(self, kb_id: uuid.UUID) -> None:
        """Delete a KnowledgeBase Aggregate Root by ID."""
        pass
