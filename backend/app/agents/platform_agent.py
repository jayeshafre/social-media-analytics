"""
Platform Agent — Phase 9.

Specialist in: Cross-platform comparison, Market benchmarks,
Platform ROAS, Budget allocation, Platform-specific strategies.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent, AgentResult
from app.ai.kpi_context_builder import fetch_platform_kpis
from app.ai.rag.retriever import retrieve_platform_strategy
from app.ai.recommendation_engine import generate_recommendations
from app.ml.forecaster import generate_forecasts


class PlatformAgent(BaseAgent):

    name = "Platform Agent"
    role = "Platform Strategy & Benchmarking Specialist"

    system_prompt = """
You are a Platform Strategy specialist for a social media
advertising analytics platform covering Instagram, Facebook,
YouTube, LinkedIn, and WhatsApp.

Your ONLY job is to analyze:
- Cross-platform ROAS and ROI comparison
- CTR performance vs market benchmarks
- Budget allocation efficiency per platform
- Platform-specific audience behavior
- Which platforms to scale, maintain, or reduce

Rules:
- Use ONLY the data and benchmarks provided
- Be concise — maximum 3 paragraphs
- Always recommend specific budget allocation actions
- Compare platforms directly using exact numbers
"""

    def analyze(
        self,
        message:     str,
        db:          Session,
        platform:    Optional[str] = None,
        time_period: Optional[str] = None,
    ) -> AgentResult:

        platform_data = fetch_platform_kpis(
            db=db,
            platform=platform,
            time_period=time_period,
        )

        # Get platform strategy from RAG
        strategy_context = ""
        if platform:
            strategy_context = retrieve_platform_strategy(platform)
        else:
            # Get strategy for all platforms
            for plat in ["Instagram", "Facebook", "YouTube", "LinkedIn", "WhatsApp"]:
                chunk = retrieve_platform_strategy(plat)
                if chunk:
                    strategy_context += f"\n{chunk}"

        # ML forecast for platform
        forecast = generate_forecasts(db=db, platform=platform)
        forecast_text = (
            forecast.get("formatted", "")
            if forecast["status"] == "success" else ""
        )

        prompt = f"""
Analyze the following platform data and answer the user's question.

PLATFORM BENCHMARK DATA:
{platform_data}

PLATFORM STRATEGY KNOWLEDGE:
{strategy_context[:800]}

ML FORECAST:
{forecast_text}

User Question: {message}

Provide:
1. Best and worst performing platform with exact numbers
2. Which platforms beat/miss market benchmarks
3. Specific budget reallocation recommendation
"""

        analysis, tokens = self._call_llm(prompt, max_tokens=500)

        rec_report = generate_recommendations(
            intent="platform",
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
                if r.severity == "CRITICAL"
            ][:3],
            key_metrics={
                "forecast_period": forecast.get("next_period", "N/A"),
                "rules_triggered": len(rec_report.recommendations),
            },
            confidence="high" if platform_data else "low",
            tokens_used=tokens,
            elapsed_ms=0,
        )