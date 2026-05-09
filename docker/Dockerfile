# ─────────────────────────────────────────────────────────
# Stage 1: Base image
# We use Python 3.11 slim — smaller image, faster builds
# ─────────────────────────────────────────────────────────
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Environment variables — prevents Python from writing .pyc files
# and buffers stdout/stderr (so logs appear immediately)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies needed for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first
# (Docker caches this layer — only re-runs if requirements.txt changes)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full backend app code
COPY backend/ .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]