"""
Unit and integration tests for VectorRetriever, MockReranker, and IngestionPipeline.
"""

import unittest

from packages.rag.ingestion import IngestionPipeline
from packages.rag.ranking import MockReranker
from packages.rag.retriever import VectorRetriever


class TestRetrievalAndIngestion(unittest.TestCase):
    def test_ingestion_pipeline_and_vector_retriever(self) -> None:
        pipeline = IngestionPipeline()
        chunks = pipeline.ingest_source("reports/tcs_annual.pdf")

        self.assertGreater(len(chunks), 0)
        self.assertIsNotNone(chunks[0].embedding)

        retriever = VectorRetriever(
            vector_store=pipeline.vector_store,
            embedding_provider=pipeline.embedding_provider,
        )

        results = retriever.retrieve("What is the ROCE and financial growth?", top_k=3)
        self.assertGreater(len(results), 0)
        self.assertIn("TCS_ANNUAL", results[0].chunk.text)

    def test_mock_reranker(self) -> None:
        pipeline = IngestionPipeline()
        pipeline.ingest_source("reports/tcs_annual.pdf")

        retriever = VectorRetriever(
            vector_store=pipeline.vector_store,
            embedding_provider=pipeline.embedding_provider,
        )
        initial_results = retriever.retrieve("ROCE growth", top_k=3)

        reranker = MockReranker()
        reranked_results = reranker.rerank("ROCE growth", initial_results)

        self.assertEqual(len(reranked_results), len(initial_results))
        self.assertEqual(reranked_results[0].rank, 1)


if __name__ == "__main__":
    unittest.main()
