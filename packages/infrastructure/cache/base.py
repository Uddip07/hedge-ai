"""
Base Cache Abstraction for Infrastructure Layer.

Defines the abstract BaseCache interface for caching data values with optional TTL.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseCache(ABC):
    """
    Abstract Base Cache Contract.
    """

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """
        Retrieve value by cache key.

        Args:
            key (str): Unique cache key identifier.

        Returns:
            Any | None: Cached value or None if key missing or expired.
        """

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> bool:
        """
        Store value in cache with optional TTL.

        Args:
            key (str): Unique cache key identifier.
            value (Any): Value to store (must be JSON serializable or primitive).
            ttl_seconds (int | None): Expiration time in seconds.

        Returns:
            bool: True if key was stored successfully.
        """

    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Remove key from cache.

        Args:
            key (str): Unique cache key identifier.

        Returns:
            bool: True if key was deleted.
        """

    @abstractmethod
    def clear(self) -> bool:
        """
        Clear all cached entries.

        Returns:
            bool: True if cache was cleared.
        """

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if non-expired key exists in cache.

        Args:
            key (str): Unique cache key identifier.

        Returns:
            bool: True if non-expired key exists.
        """
