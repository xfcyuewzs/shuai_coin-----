import time

class MemoryCache:
    """简单的内存缓存，带 TTL (过期时间)"""
    def __init__(self):
        self._cache = {}

    def set(self, key, value, ttl=60):
        self._cache[key] = {
            "value": value,
            "expiry": time.time() + ttl
        }

    def get(self, key):
        item = self._cache.get(key)
        if item:
            if time.time() < item["expiry"]:
                return item["value"]
            else:
                del self._cache[key]
        return None

    def clear(self):
        self._cache.clear()

# 全局单例
cache = MemoryCache()
