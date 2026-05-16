"""
ChromaDB Vector Store — Phase 6.

Single persistent ChromaDB instance.
Stores document embeddings for semantic search.

Same pattern as database.py:
- Create once at startup
- Reuse everywhere
- Persist to disk so embeddings survive restarts
"""

import logging
from pathlib import Path
import chromadb
from chromadb.config import Settings

logger = logging.getLogger("sma_api.vector_store")

# ─────────────────────────────────────────────────────────────
# ChromaDB persists to disk at this path
# Embeddings survive server restarts — no re-embedding needed
# ─────────────────────────────────────────────────────────────
CHROMA_PATH = Path(__file__).resolve().parents[4] / "data" / "chroma_db"
COLLECTION_NAME = "sma_knowledge_base"


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Returns a persistent ChromaDB client.
    Data stored at: data/chroma_db/
    """
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH),
        settings=Settings(anonymized_telemetry=False),
    )

    logger.info(f"ChromaDB client initialized | path={CHROMA_PATH}")
    return client


def get_or_create_collection(
    client: chromadb.PersistentClient,
) -> chromadb.Collection:
    """
    Get existing collection or create a new one.
    Collection = our knowledge base index.
    """
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine similarity for text
    )
    logger.info(
        f"Collection '{COLLECTION_NAME}' ready | "
        f"documents={collection.count()}"
    )
    return collection


# Single shared instances
chroma_client     = get_chroma_client()
knowledge_base    = get_or_create_collection(chroma_client)