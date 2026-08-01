"""
Redis Cache Adapter for Infrastructure Layer.

Connects to Redis server or gracefully falls back to MemoryCacheAdapter when Redis is unavailable.
"""

import json
from typing import Any

from packages.infrastructure.cache.base import BaseCache
from packages.infrastructure.cache.memory_cache import MemoryCacheAdapter


class RedisCacheAdapter(BaseCache):
    """
    Redis Cache Adapter implementing BaseCache.
    Provides graceful fallback to MemoryCacheAdapter if Redis server is unreachable.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0") -> None:
        self.redis_url = redis_url
        self.fallback = MemoryCacheAdapter()
        self._redis_client: Any | None = None
        self._is_connected: bool = False
        self._try_connect()

    def _try_connect(self) -> None:
        try:
            import redis

            client = redis.Redis.from_url(self.redis_url, socket_timeout=1.0)
            client.ping()
            self._redis_client = client
            self._is_connected = True
        except Exception:
            self._redis_client = None
            self._is_connected = False

    def get(self, key: str) -> Any | None:
        if self._is_connected and self._redis_client is not None:
            try:
                raw_val = self._redis_client.get(key)
                if raw_val is None:
                    return None
                return json.loads(raw_val)
            except Exception:
                pass
        return self.fallback.get(key)

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> bool:
        if self._is_connected and self._redis_client is not None:
            try:
                val_json = json.dumps(value)
                if ttl_seconds:
                    self._redis_client.setex(key, ttl_seconds, val_json)
                else:
                    self._redis_client.set(key, val_json)
                return True
            except Exception:
                pass
        return self.fallback.set(key, value, ttl_seconds)

    def delete(self, key: str) -> bool:
        if self._is_connected and self._redis_client is not None:
            try:
                res = self._redis_client.delete(key)
                return bool(res > 0)
            except Exception:
                pass
        return self.fallback.delete(key)

    def clear(self) -> bool:
        if self._is_connected and self._redis_client is not None:
            try:
                self._redis_client.flushdb()
                return True
            except Exception:
                pass
        return self.fallback.clear()

    def exists(self, key: str) -> bool:
        if self._is_connected and self._redis_client is not None:
            try:
                return bool(self._redis_client.exists(key) > 0)
            except Exception:
                pass
        return self.fallback.exists(key)
