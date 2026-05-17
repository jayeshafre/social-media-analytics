"""
Rate Limiter — Phase 10.

Sliding window rate limiting using Redis.
Prevents API abuse and controls LLM costs.

Limits (configurable via .env):
- AI chat:         20 requests per minute per IP
- Agent analysis:  10 requests per minute per IP
- ML endpoints:    30 requests per minute per IP
- RAG embed:        2 requests per minute per IP (expensive)

Strategy: Sliding window counter in Redis.
Each request increments a counter with TTL.
If counter exceeds limit → 429 Too Many Requests.
"""

import logging
from fastapi import Request, HTTPException
from app.ai.memory.redis_client import redis_client

logger = logging.getLogger("sma_api.rate_limiter")

RATE_LIMIT_PREFIX = "rl:"


def _get_client_ip(request: Request) -> str:
    """Extract client IP, respecting proxy headers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limit(
    request:     Request,
    endpoint:    str,
    max_requests: int,
    window_seconds: int = 60,
) -> dict:
    """
    Check if client has exceeded rate limit.

    Args:
        request:        FastAPI request object
        endpoint:       Endpoint identifier for the key
        max_requests:   Maximum allowed requests in window
        window_seconds: Time window in seconds

    Returns:
        dict with limit info

    Raises:
        HTTPException 429 if limit exceeded
    """
    if redis_client is None:
        # Redis unavailable — allow request (graceful degradation)
        return {"limited": False, "remaining": max_requests}

    client_ip = _get_client_ip(request)
    key       = f"{RATE_LIMIT_PREFIX}{endpoint}:{client_ip}"

    try:
        # Atomic increment
        count = redis_client.incr(key)

        # Set TTL on first request in window
        if count == 1:
            redis_client.expire(key, window_seconds)

        ttl       = redis_client.ttl(key)
        remaining = max(0, max_requests - count)

        if count > max_requests:
            logger.warning(
                f"Rate limit exceeded | ip={client_ip} | "
                f"endpoint={endpoint} | count={count}"
            )
            raise HTTPException(
                status_code=429,
                detail={
                    "error":       "Rate limit exceeded",
                    "limit":       max_requests,
                    "window":      f"{window_seconds}s",
                    "retry_after": ttl,
                    "message":     (
                        f"Maximum {max_requests} requests per "
                        f"{window_seconds}s. "
                        f"Retry after {ttl} seconds."
                    ),
                },
            )

        return {
            "limited":   False,
            "count":     count,
            "remaining": remaining,
            "ttl":       ttl,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rate limiter error: {e}")
        return {"limited": False, "remaining": max_requests}


# ─────────────────────────────────────────────────────────────
# Pre-built rate limit dependencies for each endpoint type
# Use as FastAPI Depends() in route definitions
# ─────────────────────────────────────────────────────────────
def chat_rate_limit(request: Request):
    """20 requests/minute for AI chat."""
    return check_rate_limit(request, "ai_chat", max_requests=20)


def agent_rate_limit(request: Request):
    """10 requests/minute for multi-agent (expensive)."""
    return check_rate_limit(request, "ai_agents", max_requests=10)


def ml_rate_limit(request: Request):
    """30 requests/minute for ML endpoints."""
    return check_rate_limit(request, "ai_ml", max_requests=30)


def embed_rate_limit(request: Request):
    """2 requests/minute for RAG embedding (very expensive)."""
    return check_rate_limit(request, "ai_rag_embed", max_requests=2)