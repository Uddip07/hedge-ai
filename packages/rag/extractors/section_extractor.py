"""
Section Extractor for Production RAG Ingestion Pipeline.

Parses document structure to divide text into logical section blocks.
"""

import re
from typing import Any


class SectionExtractor:
    """
    Extractor parsing markdown section headers and dividing text into structured section blocks.
    """

    def extract_sections(self, text: str) -> list[dict[str, Any]]:
        """
        Divide document text into section dictionary objects.

        Args:
            text (str): Input text payload.

        Returns:
            list[dict[str, Any]]: List of section objects (title, content, start_char, end_char).
        """
        sections: list[dict[str, Any]] = []

        # Find header matches (# Header or ## Header)
        matches = list(re.finditer(r"^(#{1,4})\s+(.+)$", text, flags=re.MULTILINE))
        if not matches:
            return [
                {
                    "title": "General",
                    "content": text.strip(),
                    "start_char": 0,
                    "end_char": len(text),
                }
            ]

        for i, match in enumerate(matches):
            title = match.group(2).strip()
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            sec_content = text[start_pos:end_pos].strip()

            sections.append(
                {
                    "title": title,
                    "content": sec_content,
                    "start_char": start_pos,
                    "end_char": end_pos,
                }
            )

        return sections
