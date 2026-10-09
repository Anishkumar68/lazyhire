import json
import logging
from typing import Any, Optional
import redis.asyncio as aioredis

from src.core.config import settings

logger = logging.getLogger("lazyhire.redis")

_redis_client: Optional[aioredis.Redis] = None


def get_redis_client() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


class RedisCache:
    """Async Redis Cache Helper with Graceful Fallback."""

    @staticmethod
    async def get_json(key: str) -> Optional[Any]:
        try:
            client = get_redis_client()
            raw_data = await client.get(key)
            if raw_data:
                return json.loads(raw_data)
        except Exception as e:
            logger.warning("Redis GET failed for key %s: %s", key, e)
        return None

    @staticmethod
    async def set_json(key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        try:
            client = get_redis_client()
            serialized = json.dumps(value, default=str)
            await client.set(key, serialized, ex=ttl_seconds)
            return True
        except Exception as e:
            logger.warning("Redis SET failed for key %s: %s", key, e)
            return False

    @staticmethod
    async def delete(key: str) -> bool:
        try:
            client = get_redis_client()
            await client.delete(key)
            return True
        except Exception as e:
            logger.warning("Redis DELETE failed for key %s: %s", key, e)
            return False
