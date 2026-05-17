# backend/app/main.py
"""
FastAPI Application Entry Point
All routers registered here.
Includes structured logging for production observability.
"""

import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.db.database import check_db_connection
from app.api import revenue, campaigns, platforms, audience, intelligence, engagement, ai_chat, ai_executive
from app.api import (
    revenue, campaigns, platforms, audience,
    intelligence, engagement, ai_chat, ai_executive, ai_rag
)
from app.ai.memory.redis_client import check_redis_connection
from app.api import (
    revenue, campaigns, platforms, audience, intelligence,
    engagement, ai_chat, ai_executive, ai_rag, ai_ml
)
from app.api import (
    revenue, campaigns, platforms, audience, intelligence,
    engagement, ai_chat, ai_executive, ai_rag, ai_ml, ai_agents
)

# ─────────────────────────────────────────
# Logging setup
# ─────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("sma_api")


# ─────────────────────────────────────────
# App initialisation
# ─────────────────────────────────────────
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ─────────────────────────────────────────
# Request logging middleware
# Logs every request: method, path, status, duration
# ─────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    logger.info(
        f"{request.method} {request.url.path} "
        f"→ {response.status_code} [{duration}ms]"
    )
    return response


# ─────────────────────────────────────────
# Global exception handler
# Returns clean JSON instead of raw 500 HTML
# ─────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error — check server logs",
            "data": None,
        },
    )


# ─────────────────────────────────────────
# CORS — allow dashboard/Power BI to call the API
# ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_methods=["GET", "POST", "DELETE"],  
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# Register all routers
# ─────────────────────────────────────────
app.include_router(revenue.router,      prefix="/api/v1")
app.include_router(campaigns.router,    prefix="/api/v1")
app.include_router(platforms.router,    prefix="/api/v1")
app.include_router(audience.router,     prefix="/api/v1")
app.include_router(intelligence.router, prefix="/api/v1")
app.include_router(engagement.router,   prefix="/api/v1") 
app.include_router(ai_chat.router, prefix="/api/v1")  # ← NEW
app.include_router(ai_executive.router, prefix="/api/v1")  # ← NEW
app.include_router(ai_rag.router, prefix="/api/v1")
app.include_router(ai_ml.router, prefix="/api/v1")
app.include_router(ai_agents.router, prefix="/api/v1")

# ─────────────────────────────────────────
# Startup / shutdown events
# ─────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    db_ok = check_db_connection()
    if db_ok:
        logger.info("✅ Database connection verified on startup")
    else:
        logger.error("❌ Database unreachable on startup — check DB config")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 API server shutting down")


# ─────────────────────────────────────────
# Health endpoints
# ─────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    db_ok    = check_db_connection()
    redis_ok = check_redis_connection()

    return {
        "api":         "healthy",
        "database":    "connected" if db_ok    else "unreachable",
        "redis":       "connected" if redis_ok else "unreachable",
        "environment": settings.APP_ENV,
    }


@app.get("/health", tags=["Health"])
def health_check():
    db_ok = check_db_connection()
    status = "connected" if db_ok else "unreachable"
    logger.info(f"Health check — DB: {status}")
    return {
        "api": "healthy",
        "database": status,
        "environment": settings.APP_ENV,
    }