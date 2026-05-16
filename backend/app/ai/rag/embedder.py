"""
Document Embedder — Phase 6.

Reads documents → splits into chunks → embeds → stores in ChromaDB.

Documents embedded:
- docs/kpi_definitions.md       (KPI formulas, benchmarks, definitions)
- docs/business_requirements.md (business questions, dashboard specs)
- docs/marketing_playbook.md    (campaign optimization strategies)

Run this once. ChromaDB persists embeddings to disk.
Re-run only when documents change.
"""

import logging
import hashlib
from pathlib import Path
from typing import Optional
from sentence_transformers import SentenceTransformer
from app.ai.rag.vector_store import knowledge_base

logger = logging.getLogger("sma_api.embedder")

# ─────────────────────────────────────────────────────────────
# Embedding model
# all-MiniLM-L6-v2: fast, free, 384-dimensional vectors
# Good for semantic similarity on business/marketing text
# Downloads automatically on first run (~80MB)
# ─────────────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
_model: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """Lazy-load the embedding model — only loads when first needed."""
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully")
    return _model


# ─────────────────────────────────────────────────────────────
# Document paths
# ─────────────────────────────────────────────────────────────
DOCS_PATH = Path(__file__).resolve().parents[5] / "docs"

DOCUMENTS = {
    "kpi_definitions": {
        "path": DOCS_PATH / "kpi_definitions.md",
        "description": "KPI definitions, formulas, benchmarks, and platform comparison",
    },
    "business_requirements": {
        "path": DOCS_PATH / "business_requirements.md",
        "description": "Business questions, dashboard requirements, platform analytics goals",
    },
    "marketing_playbook": {
        "path": DOCS_PATH / "marketing_playbook.md",
        "description": "Campaign optimization strategies, platform guides, seasonal tips",
    },
}


# ─────────────────────────────────────────────────────────────
# Chunking strategy
# We split by double newline (paragraph breaks) rather than
# fixed character count — preserves semantic meaning per chunk.
# Each KPI definition stays together. Each strategy section stays together.
# ─────────────────────────────────────────────────────────────
def _chunk_document(
    text: str,
    doc_name: str,
    max_chunk_size: int = 600,
) -> list[dict]:
    """
    Split document into semantically meaningful chunks.

    Strategy:
    - Split by double newline (paragraph/section boundaries)
    - Merge short paragraphs to avoid tiny useless chunks
    - Split oversized paragraphs at sentence boundaries
    - Each chunk tagged with source document name

    Returns list of {text, doc_name, chunk_index}
    """
    # Split on double newlines — natural section breaks in markdown
    raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks      = []
    buffer      = ""
    chunk_index = 0

    for para in raw_paragraphs:
        # Skip markdown table separator lines
        if set(para.replace("|", "").replace("-", "").strip()) == set():
            continue

        # If adding this paragraph keeps us under limit — merge
        if len(buffer) + len(para) < max_chunk_size:
            buffer = f"{buffer}\n\n{para}".strip()
        else:
            # Save current buffer as a chunk
            if buffer:
                chunks.append({
                    "text":        buffer,
                    "doc_name":    doc_name,
                    "chunk_index": chunk_index,
                })
                chunk_index += 1
            buffer = para

    # Don't forget the last buffer
    if buffer:
        chunks.append({
            "text":        buffer,
            "doc_name":    doc_name,
            "chunk_index": chunk_index,
        })

    logger.info(f"'{doc_name}' → {len(chunks)} chunks")
    return chunks


def _make_chunk_id(doc_name: str, chunk_index: int, text: str) -> str:
    """
    Generate stable unique ID for each chunk.
    Based on content hash — same content always gets same ID.
    This prevents duplicate embeddings on re-runs.
    """
    content      = f"{doc_name}_{chunk_index}_{text[:100]}"
    return hashlib.md5(content.encode()).hexdigest()


# ─────────────────────────────────────────────────────────────
# Main embedding function
# ─────────────────────────────────────────────────────────────
def embed_all_documents(force_reembed: bool = False) -> dict:
    """
    Read all documents, chunk them, embed them, store in ChromaDB.

    Args:
        force_reembed: If True, re-embeds even if already stored.
                       Use when documents change.

    Returns:
        Summary dict with counts per document.
    """
    model   = get_embedding_model()
    summary = {}

    for doc_key, doc_info in DOCUMENTS.items():
        doc_path = doc_info["path"]

        if not doc_path.exists():
            logger.warning(f"Document not found: {doc_path}")
            summary[doc_key] = {"status": "file_not_found", "chunks": 0}
            continue

        logger.info(f"Processing: {doc_path.name}")
        text   = doc_path.read_text(encoding="utf-8")
        chunks = _chunk_document(text, doc_key)

        embedded_count = 0
        skipped_count  = 0

        for chunk in chunks:
            chunk_id = _make_chunk_id(
                chunk["doc_name"],
                chunk["chunk_index"],
                chunk["text"],
            )

            # Check if already exists — skip if not force re-embedding
            if not force_reembed:
                try:
                    existing = knowledge_base.get(ids=[chunk_id])
                    if existing["ids"]:
                        skipped_count += 1
                        continue
                except Exception:
                    pass

            # Generate embedding
            vector = model.encode(chunk["text"]).tolist()

            # Store in ChromaDB
            knowledge_base.upsert(
                ids=[chunk_id],
                embeddings=[vector],
                documents=[chunk["text"]],
                metadatas=[{
                    "doc_name":    chunk["doc_name"],
                    "chunk_index": str(chunk["chunk_index"]),
                    "source":      doc_path.name,
                    "description": doc_info["description"],
                }],
            )
            embedded_count += 1

        summary[doc_key] = {
            "status":   "success",
            "chunks":   len(chunks),
            "embedded": embedded_count,
            "skipped":  skipped_count,
        }
        logger.info(
            f"'{doc_key}' complete | "
            f"embedded={embedded_count} | skipped={skipped_count}"
        )

    total = sum(v.get("embedded", 0) for v in summary.values())
    logger.info(
        f"Embedding complete | total_new={total} | "
        f"collection_size={knowledge_base.count()}"
    )
    return summary


def get_collection_stats() -> dict:
    """Return current state of the knowledge base."""
    count = knowledge_base.count()
    return {
        "total_chunks":   count,
        "collection":     "sma_knowledge_base",
        "embedding_model": EMBEDDING_MODEL,
        "status":         "ready" if count > 0 else "empty",
    }