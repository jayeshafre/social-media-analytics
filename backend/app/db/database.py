"""
Database connection pool using SQLAlchemy.
Connection pooling = reuse connections instead of
opening a new one for every API request (much faster).
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings


# Create engine with connection pool
# pool_size=10  → keep 10 connections open and ready
# max_overflow=20 → allow 20 extra under heavy load
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,   # test connection health before using it
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injected into every API route.
    Yields a DB session and guarantees it closes after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Health check — used on startup."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False