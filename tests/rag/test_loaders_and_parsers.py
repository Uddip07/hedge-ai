"""
Unit tests for MockPDFLoader and MockDocumentParser.
"""

import unittest

from packages.rag.loaders import MockPDFLoader
from packages.rag.models import Document
from packages.rag.parsers import MockDocumentParser


class TestLoadersAndParsers(unittest.TestCase):
    def test_mock_pdf_loader(self) -> None:
        loader = MockPDFLoader()
        docs = loader.load("reports/reliance_q4.pdf")
        self.assertEqual(len(docs), 1)

        doc = docs[0]
        self.assertIsInstance(doc, Document)
        self.assertIn("RELIANCE", doc.content)
        self.assertEqual(doc.metadata.source, "reports/reliance_q4.pdf")

    def test_mock_document_parser(self) -> None:
        parser = MockDocumentParser()

        parsed_str = parser.parse("  Raw text string  ")
        self.assertEqual(parsed_str, "Raw text string")

        parsed_bytes = parser.parse(b"Bytes content")
        self.assertEqual(parsed_bytes, "Bytes content")


if __name__ == "__main__":
    unittest.main()
