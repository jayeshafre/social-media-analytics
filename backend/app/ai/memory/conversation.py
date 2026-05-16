"""
Conversation Memory Manager — Phase 7.

Manages per-session conversation history in Redis.

Key design decisions:
1. session_id is provided by the client (or auto-generated)
2. History stored as JSON list in Redis
3. TTL resets on every message — session stays alive while active
4. Max history length enforced — prevents token overflow
5. Graceful degradation — if Redis is down, works without memory

Memory format in Redis:
  key:   "conv:{session_id}"
  value: JSON list of {role, content} messages
  TTL:   REDIS_TTL_SECONDS (default 1 hour)
"""

import json
import logging
import uuid
from typing import Optional
from app.ai.memory.redis_client import redis_client
from app.core.config import settings

logger = logging.getLogger("sma_api.conversation")

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────
KEY_PREFIX      = "conv:"
MAX_HISTORY     = 10   # Keep last 10 exchanges (20 messages)
                       # Beyond this, oldest messages are dropped
                       # Prevents token overflow with long conversations


def _make_key(session_id: str) -> str:
    """Redis key for a session."""
    return f"{KEY_PREFIX}{session_id}"


def generate_session_id() -> str:
    """Generate a new unique session ID."""
    return str(uuid.uuid4())


# ─────────────────────────────────────────────────────────────
# Core memory operations
# ─────────────────────────────────────────────────────────────
def get_history(session_id: str) -> list[dict]:
    """
    Retrieve conversation history for a session.

    Returns:
        List of {role, content} message dicts.
        Empty list if no history or Redis unavailable.
    """
    if redis_client is None:
        return []

    try:
        key  = _make_key(session_id)
        data = redis_client.get(key)

        if not data:
            return []

        history = json.loads(data)
        logger.debug(
            f"History loaded | session={session_id} | "
            f"messages={len(history)}"
        )
        return history

    except Exception as e:
        logger.error(f"History retrieval error: {e}")
        return []


def save_message(
    session_id: str,
    role: str,
    content: str,
) -> bool:
    """
    Append a single message to conversation history.

    Args:
        session_id: The conversation session ID
        role:       'user' or 'assistant'
        content:    The message text

    Returns:
        True if saved successfully, False if Redis unavailable.
    """
    if redis_client is None:
        return False

    try:
        history = get_history(session_id)

        # Append new message
        history.append({"role": role, "content": content})

        # Enforce max history — drop oldest pairs first
        # We drop in pairs (user + assistant) to maintain conversation structure
        while len(history) > MAX_HISTORY * 2:
            history = history[2:]  # Drop oldest user+assistant pair

        # Save back to Redis with refreshed TTL
        key = _make_key(session_id)
        redis_client.setex(
            name=key,
            time=settings.REDIS_TTL_SECONDS,
            value=json.dumps(history),
        )

        logger.debug(
            f"Message saved | session={session_id} | "
            f"role={role} | history_length={len(history)}"
        )
        return True

    except Exception as e:
        logger.error(f"Message save error: {e}")
        return False


def save_exchange(
    session_id: str,
    user_message: str,
    assistant_message: str,
) -> bool:
    """
    Save a complete user+assistant exchange in one operation.
    More efficient than two separate save_message calls.
    """
    if redis_client is None:
        return False

    try:
        history = get_history(session_id)

        # Add both messages
        history.append({"role": "user",      "content": user_message})
        history.append({"role": "assistant", "content": assistant_message})

        # Enforce max history
        while len(history) > MAX_HISTORY * 2:
            history = history[2:]

        key = _make_key(session_id)
        redis_client.setex(
            name=key,
            time=settings.REDIS_TTL_SECONDS,
            value=json.dumps(history),
        )

        logger.info(
            f"Exchange saved | session={session_id} | "
            f"total_messages={len(history)}"
        )
        return True

    except Exception as e:
        logger.error(f"Exchange save error: {e}")
        return False


def clear_history(session_id: str) -> bool:
    """
    Clear all history for a session.
    Used when user wants to start fresh.
    """
    if redis_client is None:
        return False

    try:
        key = _make_key(session_id)
        redis_client.delete(key)
        logger.info(f"History cleared | session={session_id}")
        return True

    except Exception as e:
        logger.error(f"History clear error: {e}")
        return False


def get_session_info(session_id: str) -> dict:
    """
    Return metadata about a session without full history.
    """
    if redis_client is None:
        return {"status": "redis_unavailable", "session_id": session_id}

    try:
        key     = _make_key(session_id)
        data    = redis_client.get(key)
        ttl     = redis_client.ttl(key)
        history = json.loads(data) if data else []

        return {
            "session_id":      session_id,
            "message_count":   len(history),
            "exchange_count":  len(history) // 2,
            "ttl_seconds":     ttl,
            "status":          "active" if history else "empty",
        }

    except Exception as e:
        logger.error(f"Session info error: {e}")
        return {"status": "error", "session_id": session_id}


def format_history_for_prompt(history: list[dict]) -> str:
    """
    Format conversation history as readable text
    for injection into the system prompt.

    This gives the LLM awareness of what was discussed
    without using the messages[] API format for history
    (which would require restructuring the entire chat flow).
    """
    if not history:
        return ""

    lines = ["PREVIOUS CONVERSATION CONTEXT:"]
    for msg in history:
        role    = "User" if msg["role"] == "user" else "Assistant"
        content = msg["content"]

        # Truncate very long assistant messages for context efficiency
        if msg["role"] == "assistant" and len(content) > 400:
            content = content[:400] + "... [truncated]"

        lines.append(f"{role}: {content}")

    return "\n".join(lines)