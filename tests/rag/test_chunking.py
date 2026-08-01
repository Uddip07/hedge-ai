"""
Unit tests for FixedSizeChunker and OverlappingChunker algorithms.
"""

import unittest

from packages.rag.chunking import FixedSizeChunker, OverlappingChunker
from packages.rag.models import Document, DocumentMetadata


class TestChunking(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_text = "ABCDE" * 100  # 500 characters
        self.doc = Document(
            content=self.sample_text,
            metadata=DocumentMetadata(source="test.txt", title="Test"),
        )

    def test_fixed_size_chunker(self) -> None:
        chunker = FixedSizeChunker(chunk_size=100)
        chunks = chunker.chunk_document(self.doc)

        self.assertEqual(len(chunks), 5)
        for idx, chunk in enumerate(chunks):
            self.assertEqual(len(chunk.text), 100)
            self.assertEqual(chunk.metadata.chunk_index, idx)
            self.assertEqual(chunk.metadata.start_char, idx * 100)
            self.assertEqual(chunk.metadata.end_char, (idx + 1) * 100)

    def test_overlapping_chunker(self) -> None:
        chunker = OverlappingChunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_document(self.doc)

        # Step = 80 characters. 500 chars -> start positions: 0, 80, 160, 240, 320, 400
        self.assertEqual(len(chunks), 6)
        self.assertEqual(chunks[0].metadata.start_char, 0)
        self.assertEqual(chunks[1].metadata.start_char, 80)
        self.assertEqual(chunks[2].metadata.start_char, 160)

    def test_chunker_invalid_args_raise_value_error(self) -> None:
        with self.assertRaises(ValueError):
            FixedSizeChunker(chunk_size=0)

        with self.assertRaises(ValueError):
            OverlappingChunker(chunk_size=100, chunk_overlap=150)


if __name__ == "__main__":
    unittest.main()
