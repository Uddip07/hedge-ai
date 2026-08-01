"""
Storage Port Interface for the Application Layer.

Defines outbound port contracts for storing, retrieving, and managing document artifacts,
research reports, and binary files.
"""

from abc import ABC, abstractmethod


class StoragePort(ABC):
    """
    Abstract Outbound Port for Object Storage and Blob Persistence.
    """

    @abstractmethod
    def store_file(
        self,
        file_path: str,
        content: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Store a binary file or document artifact into persistent storage.

        Args:
            file_path (str): Logical destination path or object key.
            content (bytes): Raw binary content bytes.
            content_type (str): MIME media type identifier.

        Returns:
            str: Persistent storage URL or unique file key identifier.
        """

    @abstractmethod
    def retrieve_file(self, file_id: str) -> bytes:
        """
        Retrieve binary file content by file ID or storage key.

        Args:
            file_id (str): Unique file key or path identifier.

        Returns:
            bytes: Raw binary content bytes.

        Raises:
            PortError: If file retrieval fails or file does not exist.
        """

    @abstractmethod
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from object storage by file ID or storage key.

        Args:
            file_id (str): Unique file key or path identifier.

        Returns:
            bool: True if deletion was successful.
        """

    @abstractmethod
    def exists(self, file_id: str) -> bool:
        """
        Check if a file exists in object storage.

        Args:
            file_id (str): Unique file key or path identifier.

        Returns:
            bool: True if file exists.
        """
