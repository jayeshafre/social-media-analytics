"""
RAG Management Endpoints — Phase 6.

Endpoints:
- POST /api/v1/ai/rag/embed    → embed all documents into ChromaDB
- GET  /api/v1/ai/rag/status   → check knowledge base health
- POST /api/v1/ai/rag/search   → test semantic search directly
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.ai.rag.embedder import embed_all_documents, get_collection_stats
from app.ai.rag.retriever import retrieve_relevant_context
from app.schemas.responses import APIResponse

logger = logging.getLogger("sma_api.ai_rag")

router = APIRouter(prefix="/ai/rag", tags=["RAG Knowledge Base"])


class SearchRequest(BaseModel):
    query:     str = Field(..., min_length=3, max_length=500)
    n_results: int = Field(default=3, ge=1, le=10)


@router.post("/embed", response_model=APIResponse)
def embed_documents(force_reembed: bool = False):
    """
    Embed all knowledge documents into ChromaDB.
    Run this once after setup, then again when documents change.
    Set force_reembed=true to re-process all documents from scratch.
    """
    logger.info(f"Embedding requested | force={force_reembed}")
    try:
        summary = embed_all_documents(force_reembed=force_reembed)
        stats   = get_collection_stats()

        return APIResponse(
            success=True,
            message="Documents embedded successfully",
            data={
                "embedding_summary": summary,
                "collection_stats":  stats,
            },
        )
    except Exception as e:
        logger.error(f"Embedding error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Embedding failed: {str(e)}",
        )


@router.get("/status", response_model=APIResponse)
def rag_status():
    """Check the current state of the RAG knowledge base."""
    try:
        stats = get_collection_stats()
        return APIResponse(
            success=True,
            message="RAG knowledge base status retrieved",
            data=stats,
        )
    except Exception as e:
        logger.error(f"RAG status error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=APIResponse)
def semantic_search(request: SearchRequest):
    """
    Test semantic search against the knowledge base.
    Use this to verify RAG is retrieving relevant chunks.
    """
    try:
        result = retrieve_relevant_context(
            query=request.query,
            n_results=request.n_results,
        )
        return APIResponse(
            success=True,
            message="Semantic search complete",
            data={
                "query":   request.query,
                "context": result or "No relevant chunks found",
            },
        )
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))