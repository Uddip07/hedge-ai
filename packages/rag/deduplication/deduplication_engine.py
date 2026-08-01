"""
Deduplication Engine for Production RAG Ingestion Pipeline.

Calculates content hash signatures and filters exact/near-duplicate documents during ingestion.
"""

import hashlib


class DeduplicationEngine:
    """
    Engine preventing duplicate document ingestion.
    """

    def __init__(self) -> None:
        self._seen_hashes: set[str] = set()

    def compute_hash(self, content: str) -> str:
        """Calculate SHA-256 digest string for text content."""
        clean_bytes = content.strip().encode("utf-8")
        return hashlib.sha256(clean_bytes).hexdigest()

    def is_duplicate(self, content: str) -> bool:
        """Return True if content signature has already been registered."""
        digest = self.compute_hash(content)
        return digest in self._seen_hashes

    def register_content(self, content: str) -> str:
        """Register content hash into seen set and return digest signature."""
        digest = self.compute_hash(content)
        self._seen_hashes.add(digest)
        return digest

    def clear(self) -> None:
        """Clear registered content hash history."""
        self._seen_hashes.clear()
