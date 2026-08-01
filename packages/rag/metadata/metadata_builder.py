"""
Metadata Builder for Production RAG Ingestion Pipeline.

Constructs enriched document and chunk metadata retaining mandatory compliance attributes:
document_id, company, ticker, filing_type, section, page, and publication_date.
"""

from datetime import UTC, datetime
from typing import Any

from packages.domain.value_objects.identifiers.uuid_wrappers import DocumentId
from packages.rag.models.chunk import ChunkMetadata
from packages.rag.models.document import DocumentMetadata


class MetadataBuilder:
    """
    Builder attaching mandatory hedge fund metadata attributes to document chunks.
    """

    SUPPORTED_FILING_TYPES = {
        "ANNUAL_REPORT",
        "QUARTERLY_RESULTS",
        "INVESTOR_PRESENTATION",
        "EARNINGS_TRANSCRIPT",
        "CORPORATE_ANNOUNCEMENT",
        "SEBI_FILING",
    }

    def build_document_metadata(
        self,
        source: str,
        title: str,
        company: str = "Reliance Industries Ltd",
        ticker: str = "RELIANCE.NS",
        filing_type: str = "ANNUAL_REPORT",
        publication_date: str | None = None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> DocumentMetadata:
        """Construct DocumentMetadata instance."""
        f_type = filing_type.upper()
        if f_type not in self.SUPPORTED_FILING_TYPES:
            f_type = "CORPORATE_ANNOUNCEMENT"

        pub_date = publication_date or datetime.now(UTC).strftime("%Y-%m-%d")
        extra = extra_metadata or {}
        extra.update(
            {
                "company": company,
                "ticker": ticker,
                "filing_type": f_type,
                "publication_date": pub_date,
            }
        )

        return DocumentMetadata(
            source=source,
            title=title,
            author=extra.get("author", "HedgeFundAI Pipeline"),
            file_type=extra.get("file_type", "pdf"),
        )

    def build_chunk_metadata(
        self,
        chunk_id: str,
        document_id: DocumentId,
        chunk_index: int,
        start_char: int,
        end_char: int,
        company: str = "Reliance Industries Ltd",
        ticker: str = "RELIANCE.NS",
        filing_type: str = "ANNUAL_REPORT",
        section: str = "General",
        page: int = 1,
        publication_date: str | None = None,
        token_count: int = 0,
        extra_metadata: dict[str, Any] | None = None,
    ) -> ChunkMetadata:
        """Construct ChunkMetadata containing mandatory retained filing attributes."""
        f_type = filing_type.upper()
        if f_type not in self.SUPPORTED_FILING_TYPES:
            f_type = "CORPORATE_ANNOUNCEMENT"

        pub_date = publication_date or datetime.now(UTC).strftime("%Y-%m-%d")

        return ChunkMetadata(
            chunk_id=chunk_id,
            document_id=document_id,
            chunk_index=chunk_index,
            start_char=start_char,
            end_char=end_char,
            token_count=token_count,
            company=company,
            ticker=ticker,
            filing_type=f_type,
            section=section,
            page=page,
            publication_date=pub_date,
            custom_metadata=extra_metadata or {},
        )
