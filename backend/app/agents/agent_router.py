"""
Agent Router — Phase 9.

Determines which specialist agents to activate
for a given question and intent.

Design principle:
- Simple questions activate 1-2 agents
- Complex cross-domain questions activate 3-4 agents
- Always activate the most relevant agent
- The coordinator always runs last

Agent activation map:
intent          → primary agents
─────────────────────────────────────
revenue         → Revenue + Platform
campaign        → Campaign + Revenue
audience        → Audience + Campaign
platform        → Platform + Revenue
engagement      → Campaign + Audience
anomaly         → Revenue + Campaign + Platform
general         → Revenue + Platform (defaults)
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.agents.base_agent import AgentResult
from app.agents.revenue_agent import RevenueAgent
from app.agents.campaign_agent import CampaignAgent
from app.agents.audience_agent import AudienceAgent
from app.agents.platform_agent import PlatformAgent
from app.agents.coordinator_agent import CoordinatorAgent

logger = logging.getLogger("sma_api.agent_router")

# Single instances — reused across requests
_revenue_agent  = RevenueAgent()
_campaign_agent = CampaignAgent()
_audience_agent = AudienceAgent()
_platform_agent = PlatformAgent()
_coordinator    = CoordinatorAgent()

# Intent → agent activation map
AGENT_MAP = {
    "revenue":    [_revenue_agent, _platform_agent],
    "campaign":   [_campaign_agent, _revenue_agent],
    "audience":   [_audience_agent, _campaign_agent],
    "platform":   [_platform_agent, _revenue_agent],
    "engagement": [_campaign_agent, _audience_agent],
    "anomaly":    [_revenue_agent, _campaign_agent, _platform_agent],
    "general":    [_revenue_agent, _platform_agent],
}


def run_agents(
    message:     str,
    intent:      str,
    db:          Session,
    platform:    Optional[str] = None,
    time_period: Optional[str] = None,
    session_id:  Optional[str] = None,
) -> dict:
    """
    Activate relevant agents, run them, then coordinate.

    Args:
        message:     Original user question
        intent:      Detected intent category
        db:          SQLAlchemy session
        platform:    Detected platform
        time_period: Detected time period
        session_id:  For conversation memory in coordinator

    Returns:
        Dict with final answer and agent metadata
    """
    agents = AGENT_MAP.get(intent, AGENT_MAP["general"])

    logger.info(
        f"Activating agents | intent={intent} | "
        f"agents={[a.name for a in agents]}"
    )

    # Run all specialist agents
    agent_results: list[AgentResult] = []
    for agent in agents:
        result = agent._safe_analyze(
            message=message,
            db=db,
            platform=platform,
            time_period=time_period,
        )
        agent_results.append(result)
        logger.info(
            f"{agent.name} done | "
            f"tokens={result.tokens_used} | "
            f"elapsed={result.elapsed_ms}ms"
        )

    # Run coordinator to synthesize
    final = _coordinator.synthesize(
        message=message,
        agent_results=agent_results,
        session_id=session_id,
        platform=platform,
    )

    # Build metadata
    agent_metadata = [
        {
            "agent":      r.agent_name,
            "confidence": r.confidence,
            "tokens":     r.tokens_used,
            "elapsed_ms": r.elapsed_ms,
            "error":      r.error,
        }
        for r in agent_results
    ]

    return {
        "answer":           final.analysis,
        "agents_activated": final.key_metrics.get("agents_activated", 0),
        "agents_list":      final.key_metrics.get("agents_list", ""),
        "total_tokens":     final.key_metrics.get("total_tokens", 0),
        "elapsed_ms":       final.elapsed_ms,
        "agent_details":    agent_metadata,
    }