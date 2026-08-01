"""
HTML Parser for Production RAG Ingestion Pipeline.

Strips HTML markup and converts web disclosures into clean markdown text.
"""

import re

from packages.rag.parsers.base import BaseDocumentParser


class HTMLParser(BaseDocumentParser):
    """
    Parser stripping HTML tags and extracting textual content.
    """

    def parse(self, content_stream_or_path: str | bytes) -> str:
        """Parse raw HTML string or bytes into clean markdown text."""
        if isinstance(content_stream_or_path, bytes):
            html_text = content_stream_or_path.decode("utf-8", errors="ignore")
        else:
            html_text = str(content_stream_or_path)

        # Strip HTML tags
        clean_text = re.sub(r"<[^>]+>", " ", html_text)
        lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
        return "\n".join(lines)
