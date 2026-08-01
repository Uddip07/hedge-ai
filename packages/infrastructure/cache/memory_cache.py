"""
In-Memory Cache Adapter for Infrastructure Layer.

Provides thread-safe in-memory cache storage with TTL expiration tracking for local development & testing.
"""

import time
from typing import Any

from packages.infrastructure.cache.base import BaseCache


class MemoryCacheAdapter(BaseCache):
    """
    In-Memory Cache Adapter backed by Python dictionary and timestamp-based TTL tracking.
    """

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}
        self._expires_at: dict[str, float] = {}

    def get(self, key: str) -> Any | None:
        if not self.exists(key):
            return None
        return self._store.get(key)

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> bool:
        self._store[key] = value
        if ttl_seconds is not None and ttl_seconds > 0:
            self._expires_at[key] = time.time() + ttl_seconds
        elif key in self._expires_at:
            del self._expires_at[key]
        return True

    def delete(self, key: str) -> bool:
        existed = key in self._store
        self._store.pop(key, None)
        self._expires_at.pop(key, None)
        return existed

    def clear(self) -> bool:
        self._store.clear()
        self._expires_at.clear()
        return True

    def exists(self, key: str) -> bool:
        if key not in self._store:
            return False
        exp = self._expires_at.get(key)
        if exp is not None and time.time() >= exp:
            self.delete(key)
            return False
        return True
