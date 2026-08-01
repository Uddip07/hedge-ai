"""
Unit tests for MockEmbeddingAdapter and InMemoryVectorStoreAdapter.
"""

import unittest

from packages.domain.value_objects.identifiers import DocumentId
from packages.rag.embeddings import MockEmbeddingAdapter
from packages.rag.models import Chunk, ChunkMetadata
from packages.rag.vector_store import InMemoryVectorStoreAdapter


class TestEmbeddingsAndVectorStore(unittest.TestCase):
    def setUp(self) -> None:
        self.embedding_provider = MockEmbeddingAdapter(vector_dimension=64)
        self.vector_store = InMemoryVectorStoreAdapter()

    def test_mock_embedding_adapter(self) -> None:
        self.assertEqual(self.embedding_provider.dimension, 64)

        vec = self.embedding_provider.embed_text("RELIANCE Q4 ROCE Growth")
        self.assertEqual(len(vec), 64)

        batch_vecs = self.embedding_provider.embed_batch(["Text 1", "Text 2"])
        self.assertEqual(len(batch_vecs), 2)
        self.assertEqual(len(batch_vecs[0]), 64)

    def test_in_memory_vector_store_search(self) -> None:
        doc_id = DocumentId.generate()
        vec_1 = self.embedding_provider.embed_text("High ROCE balance sheet growth")
        vec_2 = self.embedding_provider.embed_text("Risk management stop loss limit")

        c1 = Chunk(
            chunk_id="c1",
            document_id=doc_id,
            text="High ROCE balance sheet growth",
            metadata=ChunkMetadata(
                chunk_id="c1", document_id=doc_id, chunk_index=0, start_char=0, end_char=30
            ),
            embedding=vec_1,
        )
        c2 = Chunk(
            chunk_id="c2",
            document_id=doc_id,
            text="Risk management stop loss limit",
            metadata=ChunkMetadata(
                chunk_id="c2", document_id=doc_id, chunk_index=1, start_char=0, end_char=30
            ),
            embedding=vec_2,
        )

        self.vector_store.add_chunks([c1, c2])

        # Search with exact query matching c1 text
        q_vec = self.embedding_provider.embed_text("High ROCE balance sheet growth")
        results = self.vector_store.search(q_vec, top_k=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].chunk.chunk_id, "c1")
        self.assertAlmostEqual(results[0].score, 1.0, places=4)

        self.vector_store.clear()
        self.assertEqual(len(self.vector_store.search(q_vec)), 0)


if __name__ == "__main__":
    unittest.main()
