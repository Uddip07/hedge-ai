"""
Base Document Parser Abstraction for RAG Framework.

Defines standard interface for parsing raw binary/structured content into clean text.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseDocumentParser(ABC):
    """
    Abstract Base Class for Document Parsers.
    """

    @abstractmethod
    def parse(self, raw_content: Any) -> str:
        """
        Parse raw input payload into normalized text.

        Args:
            raw_content (Any): Raw document binary or object.

        Returns:
            str: Extracted plain text string.
        """
