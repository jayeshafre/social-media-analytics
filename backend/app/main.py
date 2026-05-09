"""
FastAPI Application Entry Point
All routers registered here.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import check_db_connection
from app.api import revenue, campaigns, platforms, audience, intelligence

# ─────────────────────────────────────────
# App initialisation
# ─────────────────────────────────────────
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc UI
)

# CORS — allow dashboard/Power BI to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# Register all routers
# ─────────────────────────────────────────
app.include_router(revenue.router,       prefix="/api/v1")
app.include_router(campaigns.router,     prefix="/api/v1")
app.include_router(platforms.router,     prefix="/api/v1")
app.include_router(audience.router,      prefix="/api/v1")
app.include_router(intelligence.router,  prefix="/api/v1")


# ─────────────────────────────────────────
# Root & Health endpoints
# ─────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "app": settings.APP_TITLE,
        "version": settings.API_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    db_ok = check_db_connection()
    return {
        "api": "healthy",
        "database": "connected" if db_ok else "unreachable",
        "environment": settings.APP_ENV,
    }