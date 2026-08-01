"""
Ingestion Pipeline for RAG Framework.

Orchestrates document loading, parsing, chunking, embedding vector generation, and vector store indexing.
"""

from packages.rag.chunking.base import BaseChunker
from packages.rag.chunking.fixed_size import FixedSizeChunker
from packages.rag.embeddings.base import EmbeddingPort
from packages.rag.embeddings.mock_embedding_adapter import MockEmbeddingAdapter
from packages.rag.loaders.base import BaseDocumentLoader
from packages.rag.loaders.mock_pdf_loader import MockPDFLoader
from packages.rag.models.chunk import Chunk
from packages.rag.models.document import Document
from packages.rag.vector_store.base import VectorStorePort
from packages.rag.vector_store.in_memory_store import InMemoryVectorStoreAdapter


class IngestionPipeline:
    """
    End-to-end RAG ingestion pipeline assembler.
    """

    def __init__(
        self,
        loader: BaseDocumentLoader | None = None,
        chunker: BaseChunker | None = None,
        embedding_provider: EmbeddingPort | None = None,
        vector_store: VectorStorePort | None = None,
    ) -> None:
        self.loader = loader or MockPDFLoader()
        self.chunker = chunker or FixedSizeChunker()
        self.embedding_provider = embedding_provider or MockEmbeddingAdapter()
        self.vector_store = vector_store or InMemoryVectorStoreAdapter()

    def ingest_source(self, source: str) -> list[Chunk]:
        """
        Ingest a document source location into the vector store.

        Steps:
            1. Load Document entities via DocumentLoader
            2. Split Document into Chunk segments via Chunker
            3. Generate dense vector embeddings via EmbeddingPort
            4. Index Chunks into VectorStorePort

        Returns:
            list[Chunk]: List of indexed Chunk entities with embeddings.
        """
        documents = self.loader.load(source)
        return self.ingest_documents(documents)

    def ingest_documents(self, documents: list[Document]) -> list[Chunk]:
        """
        Ingest a list of Document objects directly.

        Returns:
            list[Chunk]: List of indexed Chunk entities with embeddings.
        """
        all_chunks: list[Chunk] = []

        for doc in documents:
            chunks = self.chunker.chunk_document(doc)
            if not chunks:
                continue

            texts = [c.text for c in chunks]
            vectors = self.embedding_provider.embed_batch(texts)

            for chunk, vec in zip(chunks, vectors, strict=False):
                chunk.embedding = vec
                all_chunks.append(chunk)

        if all_chunks:
            self.vector_store.add_chunks(all_chunks)

        return all_chunks
