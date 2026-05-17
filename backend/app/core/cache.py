"""
Response Cache — Phase 10.

Caches expensive AI responses in Redis.
Identical questions within TTL window return cached answers
— zero LLM cost, instant response.

Cache strategy:
- Key: hash of (message + intent + platform + time_period)
- TTL: 30 minutes (configurable)
- Only cache non-session responses (stateless queries)
- Never cache session-based responses (memory defeats the purpose)

Cache hit rate target: 20-30% of requests
(Many business questions repeat: "what is our ROAS?" etc.)
"""

import hashlib
import json
import logging
from typing import Optional
from app.ai.memory.redis_client import redis_client
from app.core.config import settings

logger = logging.getLogger("sma_api.cache")

CACHE_PREFIX = "ai_cache:"
CACHE_TTL    = 1800  # 30 minutes


def _make_cache_key(
    message:     str,
    intent:      str,
    platform:    Optional[str],
    time_period: Optional[str],
) -> str:
    """
    Generate a deterministic cache key from request parameters.
    Same question + same context = same key = cache hit.
    """
    raw = f"{message.lower().strip()}|{intent}|{platform}|{time_period}"
    return CACHE_PREFIX + hashlib.md5(raw.encode()).hexdigest()


def get_cached_response(
    message:     str,
    intent:      str,
    platform:    Optional[str]  = None,
    time_period: Optional[str]  = None,
) -> Optional[dict]:
    """
    Check Redis for a cached response.
    Returns parsed dict if found, None if miss or Redis unavailable.
    """
    if redis_client is None:
        return None

    try:
        key  = _make_cache_key(message, intent, platform, time_period)
        data = redis_client.get(key)

        if data:
            logger.info(f"Cache HIT | key={key[-8:]}")
            cached = json.loads(data)
            cached["cache_hit"] = True
            return cached

        logger.debug(f"Cache MISS | key={key[-8:]}")
        return None

    except Exception as e:
        logger.error(f"Cache read error: {e}")
        return None


def set_cached_response(
    message:     str,
    intent:      str,
    response:    dict,
    platform:    Optional[str] = None,
    time_period: Optional[str] = None,
) -> bool:
    """
    Store a response in Redis cache.
    Returns True if cached successfully.
    """
    if redis_client is None:
        return False

    try:
        key          = _make_cache_key(message, intent, platform, time_period)
        cache_data   = {**response, "cache_hit": False}

        redis_client.setex(
            name=key,
            time=CACHE_TTL,
            value=json.dumps(cache_data),
        )

        logger.info(f"Cache SET | key={key[-8:]} | ttl={CACHE_TTL}s")
        return True

    except Exception as e:
        logger.error(f"Cache write error: {e}")
        return False


def invalidate_cache(pattern: str = "*") -> int:
    """
    Invalidate cache entries matching a pattern.
    Use pattern='*' to clear all AI cache.
    Returns number of keys deleted.
    """
    if redis_client is None:
        return 0

    try:
        keys    = redis_client.keys(f"{CACHE_PREFIX}{pattern}")
        deleted = 0
        if keys:
            deleted = redis_client.delete(*keys)
        logger.info(f"Cache invalidated | deleted={deleted} keys")
        return deleted

    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")
        return 0


def get_cache_stats() -> dict:
    """Return cache statistics for monitoring."""
    if redis_client is None:
        return {"status": "redis_unavailable"}

    try:
        keys  = redis_client.keys(f"{CACHE_PREFIX}*")
        info  = redis_client.info("stats")

        return {
            "cached_responses": len(keys),
            "cache_ttl_seconds": CACHE_TTL,
            "total_commands":   info.get("total_commands_processed", 0),
            "keyspace_hits":    info.get("keyspace_hits", 0),
            "keyspace_misses":  info.get("keyspace_misses", 0),
            "hit_rate_pct": round(
                info.get("keyspace_hits", 0) * 100 /
                max(
                    info.get("keyspace_hits", 0) +
                    info.get("keyspace_misses", 0), 1
                ), 2
            ),
        }

    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        return {"status": "error"}