# ─────────────────────────────────────────────────────────────
# Stage 1: Builder
# Install dependencies in isolated layer
# ─────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────────────────────
# Stage 2: Production image
# Minimal image with only what's needed to run
# ─────────────────────────────────────────────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages \
    /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin \
    /usr/local/bin

# Copy application code
COPY backend/ .

# Copy docs for RAG embedding
COPY docs/ /docs/

# Create non-root user — never run as root in production
RUN useradd --create-home --shell /bin/bash appuser && \
    mkdir -p /data/chroma_db && \
    chown -R appuser:appuser /app /data /docs

USER appuser

# Health check — Docker monitors this
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Production startup command
# 4 workers for production (adjust based on CPU cores)
CMD ["uvicorn", "app.main:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--workers", "4", \
    "--log-level", "info", \
    "--no-access-log"]