"""
Markdown Parser for Production RAG Ingestion Pipeline.

Parses markdown structured report text.
"""

from packages.rag.parsers.base import BaseDocumentParser


class MarkdownParser(BaseDocumentParser):
    """
    Parser for markdown document content.
    """

    def parse(self, content_stream_or_path: str | bytes) -> str:
        """Parse raw markdown string or bytes."""
        if isinstance(content_stream_or_path, bytes):
            return content_stream_or_path.decode("utf-8", errors="ignore").strip()
        return str(content_stream_or_path).strip()
