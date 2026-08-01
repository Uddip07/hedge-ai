"""
Vector Retriever Implementation.

Orchestrates embedding vector generation for query text and querying VectorStorePort.
"""

from packages.rag.embeddings.base import EmbeddingPort
from packages.rag.embeddings.mock_embedding_adapter import MockEmbeddingAdapter
from packages.rag.models.search import QueryResult
from packages.rag.retriever.base import BaseRetriever
from packages.rag.vector_store.base import VectorStorePort
from packages.rag.vector_store.in_memory_store import InMemoryVectorStoreAdapter


class VectorRetriever(BaseRetriever):
    """
    Retriever performing dense vector similarity search.
    """

    def __init__(
        self,
        vector_store: VectorStorePort | None = None,
        embedding_provider: EmbeddingPort | None = None,
    ) -> None:
        self.vector_store = vector_store or InMemoryVectorStoreAdapter()
        self.embedding_provider = embedding_provider or MockEmbeddingAdapter()

    def retrieve(self, query: str, top_k: int = 5) -> list[QueryResult]:
        if not query or not query.strip():
            return []

        query_vec = self.embedding_provider.embed_text(query)
        return self.vector_store.search(query_vec, top_k=top_k)
