import redis.asyncio as redis
import json
from contextlib import asynccontextmanager
from typing import Any, Optional
from core.config import settings

# Redis connection pool
redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL, decode_responses=True
)

def get_redis_client() -> redis.Redis:
    return redis.Redis(connection_pool=redis_pool)

class CacheService:
    def __init__(self):
        self.redis = get_redis_client()
        self.ttl = settings.CACHE_TTL_MINUTES * 60

    async def get(self, key: str) -> Optional[Any]:
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: Any) -> None:
        await self.redis.setex(key, self.ttl, json.dumps(value))

    @asynccontextmanager
    async def lock(self, lock_name: str, timeout: int = 10):
        # Cache Stampede Protection via Redis Lock
        lock = self.redis.lock(lock_name, timeout=timeout)
        acquired = await lock.acquire(blocking=True, blocking_timeout=5)
        try:
            yield acquired
        finally:
            if acquired:
                await lock.release()

cache_service = CacheService()
