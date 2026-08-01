"""
Mock Document Parser Implementation.

Parses raw content streams or bytes into clean plain text for development and tests.
"""

from typing import Any

from packages.rag.parsers.base import BaseDocumentParser


class MockDocumentParser(BaseDocumentParser):
    """
    Mock Document Parser normalizing raw content into clean text.
    """

    def parse(self, raw_content: Any) -> str:
        """
        Normalize input raw_content into string format.
        """
        if isinstance(raw_content, bytes):
            return raw_content.decode("utf-8", errors="ignore").strip()
        if isinstance(raw_content, str):
            return raw_content.strip()
        return str(raw_content).strip()
