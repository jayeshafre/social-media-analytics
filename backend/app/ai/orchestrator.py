"""
AI Orchestrator — Phase 7 update.

Now memory-aware. Loads conversation history from Redis
before processing and saves the exchange after responding.

Five intelligence layers:
1. Intent detection
2. Conversation memory load    ← NEW (Phase 7)
3. KPI context from PostgreSQL (Phase 3)
4. Rule-based recommendations  (Phase 4)
5. RAG knowledge retrieval     (Phase 6)
→ LLM response with full history
→ Save exchange to Redis       ← NEW (Phase 7)
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
from app.ai.memory.conversation import (
    get_history,
    save_exchange,
    generate_session_id,
)
from app.ml.ml_context_builder import build_ml_context

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
Use KPI definitions and real data to explain revenue performance.
Present recommendations clearly with business justification.
""",
        "campaign": f"""
ANALYTICS DOMAIN: Campaign Performance Analysis
{platform_note} {time_note}
Use campaign optimization knowledge and real data together.
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
Use real data, rule-based recommendations, and knowledge base.
Explain what changed, why it likely happened, and what to do.
Do NOT fabricate numbers.
""",
        "general": """
ANALYTICS DOMAIN: General Marketing Intelligence
Use the knowledge base context to give accurate,
definition-backed answers. Be concise and professional.
""",
    }
    return contexts.get(intent.intent, contexts["general"])


def _build_rag_query(intent: IntentResult, message: str) -> str:
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


def orchestrate(
    message:    str,
    db:         Session,
    session_id: str = None,
) -> dict:
    """
    Central orchestration — Phase 7.

    Five intelligence layers + memory:
    1. Load conversation history
    2. Detect intent
    3. Fetch real KPI data
    4. Generate recommendations
    5. Retrieve RAG knowledge
    6. Build enriched prompt
    7. Get AI response (with history)
    8. Save exchange to Redis
    """
    # Generate session ID if not provided
    if not session_id:
        session_id = generate_session_id()
        logger.info(f"New session created: {session_id}")

    # Step 1: Load conversation history
    history = get_history(session_id)
    logger.info(
        f"Session {session_id} | "
        f"history_messages={len(history)}"
    )

    # Step 2: Detect intent
    intent = detect_intent(message)

    # Step 3: Fetch real KPI data
    kpi_data = build_kpi_context(
        intent=intent.intent,
        db=db,
        platform=intent.platform,
        time_period=intent.time_period,
    )

    # Step 4: Generate recommendations
    rec_report = generate_recommendations(
        intent=intent.intent,
        db=db,
        platform=intent.platform,
        time_period=intent.time_period,
    )

    # Step 5: Retrieve RAG knowledge
    rag_query   = _build_rag_query(intent, message)
    rag_context = retrieve_relevant_context(
        query=rag_query,
        n_results=3,
    )
    if intent.platform:
        platform_strategy = retrieve_platform_strategy(intent.platform)
        if platform_strategy and platform_strategy not in rag_context:
            rag_context = f"{rag_context}\n\n{platform_strategy}"

    # Step 5b: Build ML context
    ml_context = build_ml_context(
        intent=intent.intent,
        db=db,
        platform=intent.platform,
    )

    # Step 6: Build enriched prompt
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
    if ml_context:
        prompt_parts.append(f"""
---
{ml_context}
""")

    # Add memory context note if conversation is ongoing
    if history:
        prompt_parts.append(f"""
---
NOTE: This is a continuing conversation.
You have access to the full conversation history above.
Answer the follow-up question with awareness of what was discussed.
If the user says "that platform" or "it" or "that metric",
resolve the reference from conversation history.
""")

    prompt_parts.append(f"""
---
INSTRUCTIONS:
- Use real data for all numbers — never fabricate
- Use knowledge base for definitions and strategy
- Use recommendations for specific actions
- Maintain conversation continuity from history
- Be structured, specific, and business-focused

---
User Question: {message}
""")

    enriched_message = "\n".join(prompt_parts)

    # Step 7: Get AI response — pass history for multi-turn context
    result = get_ai_response(
        user_message=enriched_message,
        history=history,
    )

    # Step 8: Save exchange to Redis
    saved = save_exchange(
        session_id=session_id,
        user_message=message,           # save original, not enriched
        assistant_message=result["answer"],
    )

    logger.info(
        f"Exchange complete | session={session_id} | "
        f"memory_saved={saved} | tokens={result['tokens_used']}"
    )

    return {
        "answer":                 result["answer"],
        "model":                  result["model"],
        "tokens_used":            result["tokens_used"],
        "session_id":             session_id,
        "intent":                 intent.intent,
        "platform_detected":      intent.platform,
        "time_period_detected":   intent.time_period,
        "confidence":             intent.confidence,
        "kpi_data_fetched":       bool(kpi_data),
        "rag_context_retrieved":  bool(rag_context),
        "recommendations_count":  len(rec_report.recommendations),
        "recommendation_summary": rec_report.summary,
        "conversation_length":    len(history) + 2,  # +2 for current exchange
        "memory_saved":           saved,
        "ml_context_generated": bool(ml_context),
    }