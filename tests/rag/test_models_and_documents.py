"""
Unit tests for RAG Document, Chunk, and DocumentManager models.
"""

import unittest

from packages.domain.value_objects.identifiers.uuid_wrappers import DocumentId
from packages.rag.documents import DocumentManager
from packages.rag.exceptions import DocumentLoadingError
from packages.rag.models import (
    Chunk,
    ChunkMetadata,
    Document,
    DocumentMetadata,
    QueryResult,
)


class TestRAGModelsAndDocuments(unittest.TestCase):
    def test_document_and_metadata_serialization(self) -> None:
        meta = DocumentMetadata(
            source="reports/reliance_2026.pdf",
            title="Reliance Q4 Report",
            author="HedgeFundAI",
        )
        doc = Document(content="Sample report text content.", metadata=meta)

        self.assertIsInstance(doc.id, DocumentId)
        d_dict = doc.to_dict()
        self.assertEqual(d_dict["metadata"]["source"], "reports/reliance_2026.pdf")
        self.assertEqual(d_dict["content"], "Sample report text content.")

    def test_chunk_and_metadata(self) -> None:
        doc_id = DocumentId.generate()
        meta = ChunkMetadata(
            chunk_id=f"{doc_id.value}-c0",
            document_id=doc_id,
            chunk_index=0,
            start_char=0,
            end_char=20,
            token_count=5,
        )
        chunk = Chunk(
            chunk_id=meta.chunk_id,
            document_id=doc_id,
            text="Sample chunk text.",
            metadata=meta,
            embedding=[0.1, 0.2, 0.3],
        )

        c_dict = chunk.to_dict()
        self.assertTrue(c_dict["has_embedding"])
        self.assertEqual(c_dict["embedding_dim"], 3)

    def test_query_result_model(self) -> None:
        doc_id = DocumentId.generate()
        meta = ChunkMetadata(
            chunk_id="c1", document_id=doc_id, chunk_index=0, start_char=0, end_char=10
        )
        chunk = Chunk(chunk_id="c1", document_id=doc_id, text="Match text", metadata=meta)
        qr = QueryResult(chunk=chunk, score=0.89543, rank=1)

        self.assertEqual(qr.to_dict()["score"], 0.8954)
        self.assertEqual(qr.to_dict()["rank"], 1)

    def test_document_manager_crud(self) -> None:
        mgr = DocumentManager()
        meta = DocumentMetadata(source="source.txt", title="Title")
        doc = Document(content="Content", metadata=meta)

        mgr.add_document(doc)
        self.assertEqual(len(mgr.list_documents()), 1)

        fetched = mgr.get_document(doc.id)
        self.assertEqual(fetched.content, "Content")

        mgr.remove_document(doc.id)
        self.assertEqual(len(mgr.list_documents()), 0)

        with self.assertRaises(DocumentLoadingError):
            mgr.get_document("non-existent-id")


if __name__ == "__main__":
    unittest.main()
