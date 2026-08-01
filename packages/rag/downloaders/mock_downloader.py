"""
Mock Document Downloader for Production RAG Ingestion Pipeline.

Simulates document retrieval for Annual Reports, Quarterly Results, Investor Presentations,
Earnings Transcripts, Corporate Announcements, and SEBI Filings.
"""

from pathlib import Path

from packages.rag.downloaders.base import DocumentDownloader
from packages.rag.models.document import Document, DocumentMetadata


class MockDocumentDownloader(DocumentDownloader):
    """
    Mock Downloader simulating local/remote file downloads for Indian equity filings.
    """

    def download(self, source_url_or_path: str) -> Document:
        """Load document from path or construct deterministic sample filing document."""
        p = Path(source_url_or_path)
        if p.exists() and p.is_file():
            content = p.read_text(encoding="utf-8")
            meta = DocumentMetadata(
                source=str(p),
                title=p.stem.replace("_", " ").title(),
                file_type=p.suffix.lstrip("."),
            )
            return Document(content=content, metadata=meta)

        # Construct deterministic sample filing document based on filename
        fn = source_url_or_path.lower()
        if "annual" in fn:
            title = "Annual Financial Report 2026"
            content = (
                "# FINANCIAL RESULTS & ANNUAL REPORT 2026\n\n"
                "## Management Discussion & Analysis\n"
                "The Company achieved strong revenue growth of 18.5% YoY. Return on Capital Employed (ROCE) expanded to 22.4%.\n\n"
                "## Financial Summary Table\n"
                "| Year | Revenue (Cr) | Profit (Cr) | ROCE |\n"
                "| 2025 | 12000 | 2400 | 20.0% |\n"
                "| 2026 | 14220 | 2900 | 22.4% |\n"
            )
        elif "quarterly" in fn:
            title = "Q4 Unaudited Financial Results"
            content = (
                "# QUARTERLY RESULTS Q4 2026\n\n"
                "## Financial Statements\n"
                "Net profit for the quarter ended March 31, 2026 increased by 14.2% YoY.\n"
            )
        elif "sebi" in fn:
            title = "SEBI Regulation 30 Disclosure"
            content = (
                "# SEBI CORPORATE DISCLOSURE\n\n"
                "## Corporate Announcement\n"
                "Disclosure under Regulation 30 of SEBI (LODR) Regulations regarding capacity expansion project.\n"
            )
        else:
            title = "Corporate Document"
            content = f"# CORPORATE DOCUMENT FOR {source_url_or_path}\n\nGeneral company overview and financial statements."

        meta = DocumentMetadata(
            source=source_url_or_path,
            title=title,
            author="HedgeFundAI Ingestion Engine",
        )
        return Document(content=content, metadata=meta)
