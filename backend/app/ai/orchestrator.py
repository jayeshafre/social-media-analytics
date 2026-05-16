"""
AI Orchestrator — Phase 6 update.

Now runs four intelligence layers:
1. Intent detection
2. KPI context from PostgreSQL  (Phase 3)
3. Rule-based recommendations   (Phase 4)
4. RAG knowledge retrieval      (Phase 6) ← NEW
"""

import logging
from sqlalchemy.orm import Session
from app.ai.intent_detector import detect_intent, IntentResult
from app.ai.chat_service import get_ai_response
from app.ai.kpi_context_builder import build_kpi_context
from app.ai.recommendation_engine import generate_recommendations
from app.ai.rag.retriever import (
    retrieve_relevant_context,
    retrieve_platform_strategy,
)

logger = logging.getLogger("sma_api.orchestrator")


def _build_domain_context(intent: IntentResult) -> str:
    platform_note = (
        f"Focus specifically on {intent.platform}."
        if intent.platform else "Consider all platforms."
    )
    time_note = (
        f"Time period in focus: {intent.time_period.replace('_', ' ')}."
        if intent.time_period else ""
    )

    contexts = {
        "revenue": f"""
ANALYTICS DOMAIN: Revenue & ROI Analysis
{platform_note} {time_note}
Use the KPI definitions and real data to explain revenue performance.
Present recommendations clearly with business justification.
""",
        "campaign": f"""
ANALYTICS DOMAIN: Campaign Performance Analysis
{platform_note} {time_note}
Use the campaign optimization knowledge and real data together.
Present actionable recommendations backed by both data and strategy.
""",
        "audience": f"""
ANALYTICS DOMAIN: Audience & Demographics Analysis
{platform_note} {time_note}
Use audience strategy knowledge and real data to identify
which segments need attention and why.
""",
        "platform": f"""
ANALYTICS DOMAIN: Platform Comparison & Benchmarking
{platform_note} {time_note}
Use platform benchmark knowledge and real data together.
Give budget allocation recommendations per platform.
""",
        "engagement": f"""
ANALYTICS DOMAIN: Engagement & Sentiment Analysis
{platform_note} {time_note}
Use platform engagement strategy and real data.
Explain engagement health and content strategy recommendations.
""",
        "anomaly": f"""
ANALYTICS DOMAIN: Anomaly Detection & Root Cause Analysis
{platform_note} {time_note}
Use real data, rule-based recommendations, AND knowledge base context.
Explain what changed, why it likely happened, and what to do.
Do NOT fabricate numbers.
""",
        "general": """
ANALYTICS DOMAIN: General Marketing Intelligence
Use the knowledge base context to give accurate, definition-backed answers.
Be concise and professional.
""",
    }
    return contexts.get(intent.intent, contexts["general"])


def _build_rag_query(intent: IntentResult, message: str) -> str:
    """
    Build the best RAG search query for this intent.
    We enrich the raw message with intent context for better retrieval.
    """
    enrichments = {
        "revenue":    f"ROI ROAS revenue profit ad spend {message}",
        "campaign":   f"campaign optimization CTR conversion rate {message}",
        "audience":   f"audience targeting demographics age group {message}",
        "platform":   f"platform strategy benchmark comparison {message}",
        "engagement": f"engagement rate sentiment content strategy {message}",
        "anomaly":    f"performance drop decline optimization {message}",
        "general":    message,
    }
    return enrichments.get(intent.intent, message)


def orchestrate(message: str, db: Session) -> dict:
    """
    Central orchestration — Phase 6.

    Four intelligence layers:
    1. Detect intent
    2. Fetch real KPI data from PostgreSQL
    3. Generate rule-based recommendations
    4. Retrieve relevant knowledge from RAG
    5. Build enriched prompt with all four layers
    6. Get AI response
    """
    # Step 1: Detect intent
    intent = detect_intent(message)

    # Step 2: Fetch real KPI data
    kpi_data = build_kpi_context(
        intent=intent.intent,
        db=db,
        platform=intent.platform,
        time_period=intent.time_period,
    )

    # Step 3: Generate recommendations
    rec_report = generate_recommendations(
        intent=intent.intent,
        db=db,
        platform=intent.platform,
        time_period=intent.time_period,
    )

    # Step 4: Retrieve RAG knowledge
    rag_query   = _build_rag_query(intent, message)
    rag_context = retrieve_relevant_context(
        query=rag_query,
        n_results=3,
    )

    # If platform detected, also fetch platform-specific strategy
    if intent.platform:
        platform_strategy = retrieve_platform_strategy(intent.platform)
        if platform_strategy and platform_strategy not in rag_context:
            rag_context = f"{rag_context}\n\n{platform_strategy}"

    # Step 5: Build fully enriched prompt
    domain_context = _build_domain_context(intent)
    prompt_parts   = [domain_context]

    if kpi_data:
        prompt_parts.append(f"""
---
REAL DATA FROM DATABASE:
{kpi_data}
""")

    if rec_report.has_recommendations():
        prompt_parts.append(f"""
---
{rec_report.formatted()}
Rule Engine Summary: {rec_report.summary}
""")

    if rag_context:
        prompt_parts.append(f"""
---
{rag_context}
""")

    prompt_parts.append(f"""
---
INSTRUCTIONS:
- Use real data for all numbers — never fabricate
- Use knowledge base context for definitions and strategy
- Use recommendations for specific actions
- Present CRITICAL items first
- Be structured, specific, and business-focused

---
User Question: {message}
""")

    enriched_message = "\n".join(prompt_parts)

    # Step 6: Get AI response
    result = get_ai_response(enriched_message)

    return {
        "answer":                 result["answer"],
        "model":                  result["model"],
        "tokens_used":            result["tokens_used"],
        "intent":                 intent.intent,
        "platform_detected":      intent.platform,
        "time_period_detected":   intent.time_period,
        "confidence":             intent.confidence,
        "kpi_data_fetched":       bool(kpi_data),
        "rag_context_retrieved":  bool(rag_context),
        "recommendations_count":  len(rec_report.recommendations),
        "recommendation_summary": rec_report.summary,
    }