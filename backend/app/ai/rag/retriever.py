"""
RAG Retriever — Phase 6.

Converts a user question into an embedding,
searches ChromaDB for the most semantically similar chunks,
and returns them formatted for prompt injection.

This is the READ side of RAG.
The embedder.py is the WRITE side.
"""

import logging
from typing import Optional
from sentence_transformers import SentenceTransformer
from app.ai.rag.vector_store import knowledge_base
from app.ai.rag.embedder import get_embedding_model

logger = logging.getLogger("sma_api.retriever")


def retrieve_relevant_context(
    query: str,
    n_results: int = 3,
    doc_filter: Optional[str] = None,
) -> str:
    """
    Search the knowledge base for chunks relevant to the query.

    Args:
        query:      The user's question or search text
        n_results:  Number of chunks to retrieve (default 3)
        doc_filter: Optional — filter to specific doc
                    ('kpi_definitions', 'business_requirements',
                     'marketing_playbook')

    Returns:
        Formatted string of relevant chunks for prompt injection.
        Empty string if nothing relevant found.
    """
    if knowledge_base.count() == 0:
        logger.warning("Knowledge base is empty — run embed_all_documents() first")
        return ""

    try:
        model  = get_embedding_model()
        vector = model.encode(query).tolist()

        # Build query kwargs
        query_kwargs = {
            "query_embeddings": [vector],
            "n_results":        min(n_results, knowledge_base.count()),
            "include":          ["documents", "metadatas", "distances"],
        }

        # Optional filter by document type
        if doc_filter:
            query_kwargs["where"] = {"doc_name": {"$eq": doc_filter}}

        results = knowledge_base.query(**query_kwargs)

        if not results["documents"] or not results["documents"][0]:
            logger.info(f"No relevant chunks found for: {query[:60]}")
            return ""

        # Format retrieved chunks for prompt injection
        chunks     = results["documents"][0]
        metadatas  = results["metadatas"][0]
        distances  = results["distances"][0]

        # Filter by relevance — cosine distance < 0.6 means relevant
        # Distance of 0 = identical, 1 = completely different
        relevant = [
            (chunk, meta, dist)
            for chunk, meta, dist in zip(chunks, metadatas, distances)
            if dist < 0.6
        ]

        if not relevant:
            logger.info(f"No sufficiently relevant chunks for: {query[:60]}")
            return ""

        lines = ["KNOWLEDGE BASE CONTEXT:"]
        for i, (chunk, meta, dist) in enumerate(relevant, 1):
            source = meta.get("source", "unknown")
            relevance = round((1 - dist) * 100, 1)
            lines.append(
                f"\n[Source: {source} | Relevance: {relevance}%]\n{chunk}"
            )

        logger.info(
            f"Retrieved {len(relevant)} relevant chunks for: "
            f"'{query[:60]}' | "
            f"best_relevance={(1-distances[0])*100:.1f}%"
        )

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Retrieval error: {e}", exc_info=True)
        return ""


def retrieve_kpi_definition(kpi_name: str) -> str:
    """
    Specialized retriever for KPI definitions.
    Always searches only the kpi_definitions document.
    Used when intent = 'general' and question contains metric names.
    """
    return retrieve_relevant_context(
        query=f"definition formula benchmark for {kpi_name}",
        n_results=2,
        doc_filter="kpi_definitions",
    )


def retrieve_platform_strategy(platform: str) -> str:
    """
    Specialized retriever for platform-specific strategy.
    Always searches the marketing playbook.
    """
    return retrieve_relevant_context(
        query=f"{platform} campaign strategy optimization best practices",
        n_results=2,
        doc_filter="marketing_playbook",
    )