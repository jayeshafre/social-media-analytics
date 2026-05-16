"""
Audience Agent — Phase 9.

Specialist in: Age groups, Device types, Gender targeting,
Income levels, Customer segmentation, Demographic performance.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent, AgentResult
from app.ai.kpi_context_builder import fetch_audience_kpis
from app.ai.rag.retriever import retrieve_relevant_context
from app.ai.recommendation_engine import generate_recommendations


class AudienceAgent(BaseAgent):

    name = "Audience Agent"
    role = "Audience & Demographics Specialist"

    system_prompt = """
You are an Audience & Demographics specialist for a social media
advertising analytics platform.

Your ONLY job is to analyze:
- Age group performance and conversion rates
- Device type effectiveness (Mobile, Desktop, Tablet)
- Gender targeting performance
- Customer segmentation and income level analysis
- Audience quality and targeting efficiency

Rules:
- Use ONLY the data provided
- Be concise — maximum 3 paragraphs
- Lead with the highest-value audience segment finding
- End with 2-3 specific audience targeting actions
"""

    def analyze(
        self,
        message:     str,
        db:          Session,
        platform:    Optional[str] = None,
        time_period: Optional[str] = None,
    ) -> AgentResult:

        audience_data = fetch_audience_kpis(
            db=db,
            platform=platform,
            time_period=time_period,
        )

        rag_context = retrieve_relevant_context(
            query=f"audience targeting demographics age group {message}",
            n_results=2,
        )

        prompt = f"""
Analyze the following audience data and answer the user's question.

AUDIENCE DATA:
{audience_data}

TARGETING KNOWLEDGE:
{rag_context}

User Question: {message}

Provide:
1. Best performing audience segment with exact metrics
2. Underperforming segment that needs attention
3. 2-3 specific audience targeting optimizations
"""

        analysis, tokens = self._call_llm(prompt, max_tokens=500)

        rec_report = generate_recommendations(
            intent="audience",
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
            ][:3],
            key_metrics={"rag_retrieved": bool(rag_context)},
            confidence="high" if audience_data else "low",
            tokens_used=tokens,
            elapsed_ms=0,
        )