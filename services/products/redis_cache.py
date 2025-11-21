import os
import json
import redis
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


class Cache:
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    @staticmethod
    def set(key: str, value: Any, expire: int = 3600):
        """Set value in cache with expiration."""
        try:
            redis_client.setex(
                key,
                expire,
                json.dumps(value, default=str)
            )
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    @staticmethod
    def delete(key: str):
        """Delete key from cache."""
        try:
            redis_client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

