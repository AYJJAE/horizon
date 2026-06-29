"""
backend/core/cache.py
Redis cache wrapper with TTL-based caching and in-memory fallback.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Simple in-memory cache for when Redis is unavailable."""

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    async def get(self, key: str) -> Optional[str]:
        return self._store.get(key)

    async def set(self, key: str, value: str, ex: int = 3600) -> None:
        self._store[key] = value

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def flush(self) -> None:
        self._store.clear()

    async def ping(self) -> bool:
        return True


_redis_client = None
_fallback_cache = InMemoryCache()


async def get_cache():
    """Return Redis client if available, otherwise in-memory fallback."""
    global _redis_client
    from backend.core.config import settings

    if not settings.use_redis:
        return _fallback_cache

    if _redis_client is None:
        try:
            import redis.asyncio as aioredis
            _redis_client = aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
            )
            await _redis_client.ping()
            logger.info("Redis cache connected: %s", settings.redis_url)
        except Exception as exc:
            logger.warning("Redis unavailable (%s), using in-memory cache.", exc)
            _redis_client = _fallback_cache

    return _redis_client


async def cache_get(key: str) -> Optional[Any]:
    """Retrieve and deserialize a cached value."""
    cache = await get_cache()
    raw = await cache.get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


async def cache_set(key: str, value: Any, ttl: int = 3600) -> None:
    """Serialize and store a value in the cache."""
    cache = await get_cache()
    try:
        serialized = json.dumps(value, default=str)
        await cache.set(key, serialized, ex=ttl)
    except Exception as exc:
        logger.warning("Cache set failed for key '%s': %s", key, exc)


async def cache_delete(key: str) -> None:
    """Remove a key from the cache."""
    cache = await get_cache()
    await cache.delete(key)


async def close_cache() -> None:
    """Close Redis connection pool gracefully."""
    global _redis_client
    if _redis_client and hasattr(_redis_client, "aclose"):
        await _redis_client.aclose()
        _redis_client = None
