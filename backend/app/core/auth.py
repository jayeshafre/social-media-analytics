"""
API Key Authentication — Phase 10.

Protects all AI endpoints with API key validation.
Keys are stored in environment variables.

Usage:
  Add header to every request:
  X-API-Key: your-secret-key

Public endpoints (no auth required):
  GET /          (root)
  GET /health    (health check)
  GET /docs      (Swagger)
  GET /redoc     (ReDoc)

All /api/v1/ai/* endpoints require authentication.
"""

import logging
import secrets
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

logger = logging.getLogger("sma_api.auth")

# FastAPI security scheme — reads X-API-Key header
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description="API key for authentication. Add to X-API-Key header.",
)


def verify_api_key(
    api_key: str = Security(api_key_header),
) -> str:
    """
    Verify the provided API key.

    Returns the API key if valid.
    Raises 401 if missing or invalid.

    Used as FastAPI dependency:
    @router.post("/chat")
    def endpoint(api_key: str = Depends(verify_api_key)):
        ...
    """
    # If no API keys configured — skip auth (development mode)
    if not settings.API_KEYS:
        return "dev_mode"

    if not api_key:
        logger.warning("Request missing API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Add X-API-Key header.",
        )

    # Constant-time comparison — prevents timing attacks
    valid_keys = [k.strip() for k in settings.API_KEYS.split(",") if k.strip()]

    for valid_key in valid_keys:
        if secrets.compare_digest(api_key, valid_key):
            logger.debug("API key validated successfully")
            return api_key

    logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid API key.",
    )


def generate_api_key(length: int = 32) -> str:
    """Generate a cryptographically secure API key."""
    return secrets.token_urlsafe(length)