"""
Overlapping Chunker Implementation.

Splits document text into overlapping character-size segments using a sliding window.
"""

from packages.rag.chunking.base import BaseChunker
from packages.rag.models.chunk import Chunk, ChunkMetadata
from packages.rag.models.document import Document


class OverlappingChunker(BaseChunker):
    """
    Sliding window chunker maintaining fixed overlap between consecutive chunks.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0.")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be non-negative and less than chunk_size.")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document: Document) -> list[Chunk]:
        content = document.content
        if not content:
            return []

        chunks: list[Chunk] = []
        doc_id = document.id
        length = len(content)
        start = 0
        idx = 0
        step = self.chunk_size - self.chunk_overlap

        while start < length:
            end = min(start + self.chunk_size, length)
            segment_text = content[start:end]

            chunk_id = f"{doc_id.value}-ov-chunk-{idx}"
            metadata = ChunkMetadata(
                chunk_id=chunk_id,
                document_id=doc_id,
                chunk_index=idx,
                start_char=start,
                end_char=end,
                token_count=max(1, len(segment_text) // 4),
            )

            chunk = Chunk(
                chunk_id=chunk_id,
                document_id=doc_id,
                text=segment_text,
                metadata=metadata,
            )
            chunks.append(chunk)

            if end == length:
                break
            start += step
            idx += 1

        return chunks
