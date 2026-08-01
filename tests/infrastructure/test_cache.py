"""
Unit tests for MemoryCacheAdapter and RedisCacheAdapter.
"""

import time
import unittest

from packages.infrastructure.cache import MemoryCacheAdapter, RedisCacheAdapter


class TestCacheInfrastructure(unittest.TestCase):
    def test_memory_cache_adapter_crud_and_ttl(self) -> None:
        cache = MemoryCacheAdapter()

        self.assertFalse(cache.exists("k1"))
        self.assertIsNone(cache.get("k1"))

        cache.set("k1", {"data": 123}, ttl_seconds=1)
        self.assertTrue(cache.exists("k1"))
        self.assertEqual(cache.get("k1"), {"data": 123})

        time.sleep(1.1)
        self.assertFalse(cache.exists("k1"))
        self.assertIsNone(cache.get("k1"))

        cache.set("k2", "val")
        self.assertTrue(cache.delete("k2"))
        self.assertFalse(cache.exists("k2"))

        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        self.assertFalse(cache.exists("a"))
        self.assertFalse(cache.exists("b"))

    def test_redis_cache_adapter_fallback(self) -> None:
        # Assuming no Redis server on default port, falls back to MemoryCacheAdapter cleanly
        cache = RedisCacheAdapter(redis_url="redis://invalid-host:6379/0")

        cache.set("rk1", "test_value")
        self.assertTrue(cache.exists("rk1"))
        self.assertEqual(cache.get("rk1"), "test_value")
        self.assertTrue(cache.delete("rk1"))
        self.assertFalse(cache.exists("rk1"))


if __name__ == "__main__":
    unittest.main()
