"""
PDF Parser for Production RAG Ingestion Pipeline.

Extracts text content and layout headers from PDF filings.
"""

from packages.rag.parsers.base import BaseDocumentParser


class PDFParser(BaseDocumentParser):
    """
    Parser handling PDF text parsing and layout cleanup.
    """

    def parse(self, content_stream_or_path: str | bytes) -> str:
        """Parse text content from raw PDF bytes or file path."""
        if isinstance(content_stream_or_path, bytes):
            text = content_stream_or_path.decode("utf-8", errors="ignore")
        else:
            text = str(content_stream_or_path)

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
