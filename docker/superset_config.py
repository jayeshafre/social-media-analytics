# docker/superset_config.py
# ─────────────────────────────────────────────────────────
# Superset configuration.
# Mounted into the container at /app/pythonpath/superset_config.py
# Superset auto-loads this file on startup.
# ─────────────────────────────────────────────────────────

import os

# ── Security ──────────────────────────────────────────────────
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "your-very-secret-key-change-this")

# ── Metadata database ─────────────────────────────────────────
# Superset stores its own config (dashboards, charts, users)
# in a separate database called superset_meta
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql+psycopg2://postgres:postgres@postgres:5432/superset_meta",
)

# ── Cache (Redis) ─────────────────────────────────────────────
CACHE_CONFIG = {
    "CACHE_TYPE":            "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX":      "superset_",
    "CACHE_REDIS_HOST":      os.environ.get("REDIS_HOST", "redis"),
    "CACHE_REDIS_PORT":      int(os.environ.get("REDIS_PORT", 6379)),
    "CACHE_REDIS_DB":        1,   # use DB 1 — DB 0 is reserved for your chat memory
}

# ── IFRAME EMBEDDING — most important setting ─────────────────
# This allows your React app to embed Superset dashboards
# in an <iframe> without being blocked by the browser.

# Allow all origins to embed (fine for local dev)
# For production, replace "*" with your frontend domain
ENABLE_PROXY_FIX    = True
SESSION_COOKIE_SAMESITE = "None"   # required for cross-origin iframe
SESSION_COOKIE_SECURE   = False  # set True in production with HTTPS

# Feature flags
FEATURE_FLAGS = {
    # Enables the "Share → Embed Dashboard" option in Superset UI
    "EMBEDDABLE_CHARTS":    True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "ALERT_REPORTS":        False,  # requires celery — skip for now
}

# Allow iframe embedding from any origin (localhost dev)
HTTP_HEADERS = {
    "X-Frame-Options": "ALLOWALL",
}

# CORS — allow React dev server to call Superset API
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers":        ["*"],
    "resources":            ["*"],
    "origins":              [
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # fallback
        "http://localhost:8088",   # Superset itself
    ],
}

# ── Row limits ────────────────────────────────────────────────
ROW_LIMIT            = 100000
SUPERSET_WEBSERVER_TIMEOUT = 300

# ── Disable CSRF for embedding (dev only) ────────────────────
WTF_CSRF_ENABLED = False