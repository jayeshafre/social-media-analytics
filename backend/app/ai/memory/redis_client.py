"""
Redis Client — Phase 7.

Single Redis connection shared across the app.
Same pattern as groq_client.py and database.py:
create once, reuse everywhere.

Redis is used exclusively for conversation memory.
Future phases may use it for caching KPI results.
"""

import logging
import redis
from app.core.config import settings

logger = logging.getLogger("sma_api.redis_client")


def get_redis_client() -> redis.Redis:
    """
    Returns a configured Redis client.
    decode_responses=True means we get strings back, not bytes.
    """
    try:
        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            decode_responses=True,   # always return str, not bytes
            socket_connect_timeout=3,
            socket_timeout=3,
        )
        # Verify connection immediately
        client.ping()
        logger.info(
            f"Redis connected | "
            f"{settings.REDIS_HOST}:{settings.REDIS_PORT}"
        )
        return client

    except redis.ConnectionError as e:
        logger.error(f"Redis connection failed: {e}")
        raise


def check_redis_connection() -> bool:
    """Health check — used in startup and health endpoint."""
    try:
        client = get_redis_client()
        client.ping()
        return True
    except Exception:
        return False


# Single shared instance
try:
    redis_client = get_redis_client()
except Exception as e:
    logger.error(
        f"Redis unavailable at startup: {e}. "
        f"Conversation memory will be disabled."
    )
    redis_client = None