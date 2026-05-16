"""
Campaign Agent — Phase 9.

Specialist in: CTR, CPC, Conversion Rate, Campaign types,
Influencer impact, Campaign objectives, Creative performance.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent, AgentResult
from app.ai.kpi_context_builder import fetch_campaign_kpis
from app.ai.rag.retriever import retrieve_relevant_context
from app.ai.recommendation_engine import generate_recommendations


class CampaignAgent(BaseAgent):

    name = "Campaign Agent"
    role = "Campaign Performance Specialist"

    system_prompt = """
You are a Campaign Performance specialist for a social media
advertising analytics platform.

Your ONLY job is to analyze:
- CTR (Click-Through Rate) performance
- CPC (Cost Per Click) efficiency
- Conversion Rate optimization
- Campaign type effectiveness (Reel, Video, Carousel, etc.)
- Campaign objective performance (Sales, Traffic, Leads)
- Influencer vs non-influencer campaign comparison

Rules:
- Use ONLY the data provided
- Be concise — maximum 3 paragraphs
- Lead with the most actionable campaign insight
- End with 2-3 specific campaign optimization actions
"""

    def analyze(
        self,
        message:     str,
        db:          Session,
        platform:    Optional[str] = None,
        time_period: Optional[str] = None,
    ) -> AgentResult:

        # Fetch campaign data
        campaign_data = fetch_campaign_kpis(
            db=db,
            platform=platform,
            time_period=time_period,
        )

        # Fetch relevant RAG knowledge
        rag_context = retrieve_relevant_context(
            query=f"campaign optimization CTR conversion rate {message}",
            n_results=2,
        )

        prompt = f"""
Analyze the following campaign data and answer the user's question.

CAMPAIGN DATA:
{campaign_data}

STRATEGY KNOWLEDGE:
{rag_context}

User Question: {message}

Provide:
1. Key campaign performance finding (with exact numbers)
2. Best and worst performing campaign type/objective
3. 2-3 specific campaign optimizations
"""

        analysis, tokens = self._call_llm(prompt, max_tokens=500)

        rec_report = generate_recommendations(
            intent="campaign",
            db=db,
            platform=platform,
            time_period=time_period,
        )

        return AgentResult(
            agent_name=self.name,
            role=self.role,
            analysis=analysis,
            recommendations=[
                r.action for r in rec_report.recommendations
                if r.severity in ("CRITICAL", "WARNING")
            ][:3],
            key_metrics={
                "rules_triggered":  len(rec_report.recommendations),
                "rag_retrieved":    bool(rag_context),
            },
            confidence="high" if campaign_data else "low",
            tokens_used=tokens,
            elapsed_ms=0,
        )