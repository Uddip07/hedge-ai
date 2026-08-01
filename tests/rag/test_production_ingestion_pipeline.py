"""
Unit and integration tests for Production Document Ingestion Pipeline.
"""

import unittest

from packages.rag.deduplication import DeduplicationEngine
from packages.rag.downloaders import MockDocumentDownloader
from packages.rag.exceptions import DocumentParsingError
from packages.rag.extractors import (
    HTMLParser,
    MarkdownParser,
    PDFParser,
    SectionExtractor,
    TableExtractor,
)
from packages.rag.metadata import MetadataBuilder
from packages.rag.models import Document, DocumentMetadata
from packages.rag.normalizers import DocumentValidator
from packages.rag.pipeline import DocumentPipeline
from packages.rag.storage import StorageManager


class TestProductionIngestionPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = DocumentPipeline()
        self.downloader = MockDocumentDownloader()
        self.validator = DocumentValidator()
        self.dedup_engine = DeduplicationEngine()
        self.metadata_builder = MetadataBuilder()
        self.storage_manager = StorageManager()

    def test_mock_document_downloader(self) -> None:
        doc = self.downloader.download("reliance_annual_report_2026.pdf")
        self.assertIsInstance(doc, Document)
        self.assertIn("FINANCIAL", doc.content.upper())

    def test_document_validator(self) -> None:
        meta = DocumentMetadata(source="test.txt", title="Test")
        valid_doc = Document(content="Valid text with sufficient characters.", metadata=meta)
        self.assertTrue(self.validator.validate(valid_doc))

        invalid_doc = Document(content="Short", metadata=meta)
        with self.assertRaises(DocumentParsingError):
            self.validator.validate(invalid_doc)

    def test_deduplication_engine(self) -> None:
        content = "Unique filing report text content for Reliance Q4."
        self.assertFalse(self.dedup_engine.is_duplicate(content))

        self.dedup_engine.register_content(content)
        self.assertTrue(self.dedup_engine.is_duplicate(content))

    def test_extractors(self) -> None:
        pdf_p = PDFParser()
        html_p = HTMLParser()
        md_p = MarkdownParser()
        tbl_ext = TableExtractor()
        sec_ext = SectionExtractor()

        text_sample = (
            "# EXECUTIVE FINANCIAL SUMMARY\n\n"
            "The company achieved 18.5% YoY growth.\n\n"
            "## Table Data\n"
            "| Metric | 2025 | 2026 |\n"
            "| Revenue | 1000 | 1185 |\n"
        )

        self.assertEqual(pdf_p.parse("Sample PDF"), "Sample PDF")
        self.assertEqual(html_p.parse("<h1>Title</h1>"), "Title")
        self.assertEqual(md_p.parse(text_sample), text_sample.strip())

        tables = tbl_ext.extract_tables(text_sample)
        self.assertEqual(len(tables), 1)
        self.assertIn("Revenue", tables[0]["raw_text"])

        sections = sec_ext.extract_sections(text_sample)
        self.assertEqual(len(sections), 2)
        self.assertEqual(sections[0]["title"], "EXECUTIVE FINANCIAL SUMMARY")

    def test_metadata_builder_retained_fields(self) -> None:
        doc = self.downloader.download("tcs_quarterly_results.pdf")
        doc_meta = self.metadata_builder.build_document_metadata(
            source="tcs_quarterly_results.pdf",
            title=doc.metadata.title,
            company="Tata Consultancy Services Ltd",
            ticker="TCS.NS",
            filing_type="QUARTERLY_RESULTS",
            publication_date="2026-04-15",
        )

        chunk_meta = self.metadata_builder.build_chunk_metadata(
            chunk_id="c1",
            document_id=doc.id,
            chunk_index=0,
            start_char=0,
            end_char=100,
            company="Tata Consultancy Services Ltd",
            ticker="TCS.NS",
            filing_type="QUARTERLY_RESULTS",
            section="Financial Results",
            page=1,
            publication_date="2026-04-15",
        )

        self.assertEqual(chunk_meta.company, "Tata Consultancy Services Ltd")
        self.assertEqual(chunk_meta.ticker, "TCS.NS")
        self.assertEqual(chunk_meta.filing_type, "QUARTERLY_RESULTS")
        self.assertEqual(chunk_meta.section, "Financial Results")
        self.assertEqual(chunk_meta.page, 1)
        self.assertEqual(chunk_meta.publication_date, "2026-04-15")

    def test_storage_manager(self) -> None:
        doc = self.downloader.download("sebi_disclosure.pdf")
        self.storage_manager.save_document(doc)

        retrieved = self.storage_manager.get_document(doc.id)
        self.assertIsNotNone(retrieved)
        assert retrieved is not None
        self.assertEqual(retrieved.id, doc.id)

    def test_document_pipeline_end_to_end(self) -> None:
        doc, chunks = self.pipeline.process_document(
            source_url_or_path="hdfc_annual_report_2026.pdf",
            company="HDFC Bank Ltd",
            ticker="HDFCBANK.NS",
            filing_type="ANNUAL_REPORT",
            publication_date="2026-06-30",
        )

        self.assertIsInstance(doc, Document)
        self.assertGreater(len(chunks), 0)

        # Verify every chunk retains mandatory metadata attributes
        for c in chunks:
            self.assertEqual(c.metadata.company, "HDFC Bank Ltd")
            self.assertEqual(c.metadata.ticker, "HDFCBANK.NS")
            self.assertEqual(c.metadata.filing_type, "ANNUAL_REPORT")
            self.assertIsNotNone(c.metadata.section)
            self.assertGreaterEqual(c.metadata.page, 1)
            self.assertEqual(c.metadata.publication_date, "2026-06-30")
            self.assertIsNotNone(c.embedding)

        # Verify duplicate detection error handling
        with self.assertRaises(DocumentParsingError):
            self.pipeline.process_document(
                source_url_or_path="hdfc_annual_report_2026.pdf",
                company="HDFC Bank Ltd",
                ticker="HDFCBANK.NS",
                filing_type="ANNUAL_REPORT",
            )


if __name__ == "__main__":
    unittest.main()
