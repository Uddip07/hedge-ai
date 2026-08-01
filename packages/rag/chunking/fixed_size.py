"""
Fixed Size Chunker Implementation.

Splits document text into non-overlapping, fixed-character size segments.
"""

from packages.rag.chunking.base import BaseChunker
from packages.rag.models.chunk import Chunk, ChunkMetadata
from packages.rag.models.document import Document


class FixedSizeChunker(BaseChunker):
    """
    Fixed-size text chunker splitting by fixed character length.
    """

    def __init__(self, chunk_size: int = 500) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0.")
        self.chunk_size = chunk_size

    def chunk_document(self, document: Document) -> list[Chunk]:
        content = document.content
        if not content:
            return []

        chunks: list[Chunk] = []
        doc_id = document.id
        length = len(content)
        start = 0
        idx = 0

        while start < length:
            end = min(start + self.chunk_size, length)
            segment_text = content[start:end]

            chunk_id = f"{doc_id.value}-chunk-{idx}"
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

            start = end
            idx += 1

        return chunks
