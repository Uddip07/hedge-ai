"""
Mock Storage Adapter for Infrastructure Layer.

In-memory object storage adapter for documents, reports, and file blobs.
"""

from packages.application.exceptions import PortError
from packages.application.ports.storage_port import StoragePort


class MockStorageAdapter(StoragePort):
    """
    Mock Adapter implementing StoragePort backed by an in-memory dictionary.
    """

    def __init__(self) -> None:
        self._store: dict[str, bytes] = {}

    def store_file(
        self,
        file_path: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        self._store[file_path] = content
        return file_path

    def retrieve_file(self, file_id: str) -> bytes:
        if file_id not in self._store:
            raise PortError(f"File not found in mock storage: '{file_id}'.")
        return self._store[file_id]

    def delete_file(self, file_id: str) -> bool:
        if file_id in self._store:
            del self._store[file_id]
            return True
        return False

    def exists(self, file_id: str) -> bool:
        return file_id in self._store
