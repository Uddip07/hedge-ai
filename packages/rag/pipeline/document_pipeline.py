"""
Production Document Ingestion Pipeline.

Orchestrates downloading, validation, duplicate detection, parsing, table/section extraction,
retained metadata construction, chunking, embedding, and vector indexing.
"""

from typing import Any

from packages.rag.chunking import BaseChunker, FixedSizeChunker
from packages.rag.deduplication import DeduplicationEngine
from packages.rag.downloaders import DocumentDownloader, MockDocumentDownloader
from packages.rag.embeddings import EmbeddingPort, MockEmbeddingAdapter
from packages.rag.exceptions import DocumentParsingError
from packages.rag.extractors import (
    HTMLParser,
    MarkdownParser,
    PDFParser,
    SectionExtractor,
    TableExtractor,
)
from packages.rag.metadata import MetadataBuilder
from packages.rag.models import Chunk, Document
from packages.rag.normalizers import DocumentValidator
from packages.rag.storage import StorageManager
from packages.rag.vector_store import InMemoryVectorStoreAdapter, VectorStorePort


class DocumentPipeline:
    """
    Production document ingestion pipeline for Indian financial filings.
    """

    def __init__(
        self,
        downloader: DocumentDownloader | None = None,
        validator: DocumentValidator | None = None,
        deduplication_engine: DeduplicationEngine | None = None,
        section_extractor: SectionExtractor | None = None,
        table_extractor: TableExtractor | None = None,
        metadata_builder: MetadataBuilder | None = None,
        chunker: BaseChunker | None = None,
        embedding_provider: EmbeddingPort | None = None,
        vector_store: VectorStorePort | None = None,
        storage_manager: StorageManager | None = None,
    ) -> None:
        self.downloader = downloader or MockDocumentDownloader()
        self.validator = validator or DocumentValidator()
        self.deduplication_engine = deduplication_engine or DeduplicationEngine()
        self.section_extractor = section_extractor or SectionExtractor()
        self.table_extractor = table_extractor or TableExtractor()
        self.metadata_builder = metadata_builder or MetadataBuilder()
        self.chunker = chunker or FixedSizeChunker(chunk_size=400)
        self.embedding_provider = embedding_provider or MockEmbeddingAdapter()
        self.vector_store = vector_store or InMemoryVectorStoreAdapter()
        self.storage_manager = storage_manager or StorageManager()

        self.pdf_parser = PDFParser()
        self.html_parser = HTMLParser()
        self.md_parser = MarkdownParser()

    def process_document(
        self,
        source_url_or_path: str,
        company: str = "Reliance Industries Ltd",
        ticker: str = "RELIANCE.NS",
        filing_type: str = "ANNUAL_REPORT",
        publication_date: str | None = None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> tuple[Document, list[Chunk]]:
        """
        Execute full document ingestion, parsing, extraction, metadata enrichment, chunking, and indexing.

        Args:
            source_url_or_path (str): Resource locator string.
            company (str): Company name.
            ticker (str): Stock ticker symbol.
            filing_type (str): Filing classification (ANNUAL_REPORT, QUARTERLY_RESULTS, etc.).
            publication_date (str | None): ISO publication date.
            extra_metadata (dict[str, Any] | None): Additional metadata map.

        Returns:
            tuple[Document, list[Chunk]]: Ingested Document and chunk list.
        """
        # 1. Download
        doc = self.downloader.download(source_url_or_path)

        # 2. Validate
        self.validator.validate(doc)

        # 3. Deduplicate
        if self.deduplication_engine.is_duplicate(doc.content):
            raise DocumentParsingError(
                f"Duplicate document detected for content source '{source_url_or_path}'.",
                context={"source": source_url_or_path},
            )
        self.deduplication_engine.register_content(doc.content)

        # 4. Extract sections & tables
        sections = self.section_extractor.extract_sections(doc.content)
        tables = self.table_extractor.extract_tables(doc.content)

        # 5. Enrich Document Metadata
        doc_meta = self.metadata_builder.build_document_metadata(
            source=source_url_or_path,
            title=doc.metadata.title,
            company=company,
            ticker=ticker,
            filing_type=filing_type,
            publication_date=publication_date,
            extra_metadata=extra_metadata,
        )
        doc.metadata = doc_meta

        # 6. Chunking
        raw_chunks = self.chunker.chunk_document(doc)

        # 7. Enrich every Chunk with mandatory retained metadata fields
        processed_chunks: list[Chunk] = []
        for idx, chunk in enumerate(raw_chunks):
            # Match section title for chunk
            sec_title = "General"
            for sec in sections:
                if sec["start_char"] <= chunk.metadata.start_char < sec["end_char"]:
                    sec_title = sec["title"]
                    break

            enriched_meta = self.metadata_builder.build_chunk_metadata(
                chunk_id=f"{doc.id.value}-c{idx}",
                document_id=doc.id,
                chunk_index=idx,
                start_char=chunk.metadata.start_char,
                end_char=chunk.metadata.end_char,
                company=company,
                ticker=ticker,
                filing_type=filing_type,
                section=sec_title,
                page=(idx // 3) + 1,  # Page estimation
                publication_date=publication_date,
                token_count=chunk.metadata.token_count,
                extra_metadata=extra_metadata,
            )

            # Generate dense embedding vector
            vec = self.embedding_provider.embed_text(chunk.text)

            chunk.metadata = enriched_meta
            chunk.embedding = vec
            processed_chunks.append(chunk)

        # 8. Index into VectorStore and StorageManager
        self.vector_store.add_chunks(processed_chunks)
        self.storage_manager.save_document(
            doc, extractions={"sections": sections, "tables": tables}
        )
        self.storage_manager.save_chunks(processed_chunks)

        return doc, processed_chunks
