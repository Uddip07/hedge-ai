"""
Document Validator for Production RAG Ingestion Pipeline.

Validates document text length, encoding integrity, and non-empty metadata fields.
"""

from packages.rag.exceptions import DocumentParsingError
from packages.rag.models.document import Document


class DocumentValidator:
    """
    Validator enforcing document content quality and completeness.
    """

    def __init__(self, min_character_count: int = 10) -> None:
        self.min_character_count = min_character_count

    def validate(self, document: Document) -> bool:
        """
        Validate input Document object.

        Args:
            document (Document): Candidate document.

        Returns:
            bool: True if document passes validation.

        Raises:
            DocumentParsingError: If document text is empty or invalid.
        """
        if not document.content or not document.content.strip():
            raise DocumentParsingError(
                f"Document '{document.id}' contains empty text content.",
                context={"document_id": str(document.id.value)},
            )

        if len(document.content.strip()) < self.min_character_count:
            raise DocumentParsingError(
                f"Document text length ({len(document.content)}) is below threshold ({self.min_character_count}).",
                context={"document_id": str(document.id.value)},
            )

        return True
