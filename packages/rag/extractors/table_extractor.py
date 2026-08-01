"""
Table Extractor for Production RAG Ingestion Pipeline.

Identifies and extracts tabular financial data from report text.
"""

import re
from typing import Any


class TableExtractor:
    """
    Extractor identifying pipe-delimited or tabular financial blocks.
    """

    def extract_tables(self, text: str) -> list[dict[str, Any]]:
        """
        Extract all markdown or pipe-delimited tables from text.

        Args:
            text (str): Document body text.

        Returns:
            list[dict[str, Any]]: List of extracted table dicts containing raw_text, headers, rows.
        """
        tables: list[dict[str, Any]] = []

        # Find markdown table patterns (| col1 | col2 |)
        table_blocks = re.findall(r"(\|(?:[^\n]+\|\n?)+)", text)
        for idx, block in enumerate(table_blocks):
            lines = [line.strip() for line in block.strip().splitlines() if line.strip()]
            if len(lines) >= 2:
                headers = [c.strip() for c in lines[0].split("|") if c.strip()]
                rows: list[list[str]] = []
                for line in lines[1:]:
                    if "---" in line:
                        continue
                    row_cols = [c.strip() for c in line.split("|") if c.strip()]
                    if row_cols:
                        rows.append(row_cols)

                tables.append(
                    {
                        "table_id": f"table-{idx + 1}",
                        "raw_text": block.strip(),
                        "headers": headers,
                        "rows": rows,
                    }
                )

        return tables
