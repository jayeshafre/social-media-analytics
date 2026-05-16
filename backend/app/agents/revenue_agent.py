"""
Revenue Agent — Phase 9.

Specialist in: ROI, ROAS, Revenue trends, Profitability,
CAC, Refund analysis, Budget efficiency.

Data sources used:
- PostgreSQL revenue KPIs
- ML forecasts
- Rule engine (revenue rules only)
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.agents.base_agent import BaseAgent, AgentResult
from app.ai.kpi_context_builder import fetch_revenue_kpis
from app.ai.recommendation_engine import (
    generate_recommendations,
    THRESHOLDS,
    _f,
)
from app.ml.forecaster import generate_forecasts

logger = logging.getLogger("sma_api.agent.revenue")


class RevenueAgent(BaseAgent):

    name = "Revenue Agent"
    role = "Revenue & Profitability Specialist"

    system_prompt = """
You are a Revenue & Profitability specialist for a multi-platform
social media advertising analytics system.

Your ONLY job is to analyze:
- ROI (Return on Investment)
- ROAS (Return on Ad Spend)
- Revenue trends and changes
- Profit margins and ad spend efficiency
- Customer Acquisition Cost (CAC)
- Budget allocation and efficiency

Rules:
- Use ONLY the data provided — never fabricate numbers
- Be concise — maximum 3 paragraphs
- Always state the most critical revenue finding first
- End with 2-3 specific revenue optimization actions
- Use exact numbers from the data
"""

    def analyze(
        self,
        message:     str,
        db:          Session,
        platform:    Optional[str] = None,
        time_period: Optional[str] = None,
    ) -> AgentResult:

        # Fetch revenue data
        revenue_data = fetch_revenue_kpis(
            db=db,
            platform=platform,
            time_period=time_period,
        )

        # Fetch ML forecast
        forecast = generate_forecasts(db=db, platform=platform)
        forecast_text = (
            forecast.get("formatted", "")
            if forecast["status"] == "success" else ""
        )

        # Build agent prompt
        prompt = f"""
Analyze the following revenue data and answer the user's question.

REVENUE DATA:
{revenue_data}

ML FORECAST:
{forecast_text}

User Question: {message}

Provide:
1. Key revenue findings (2-3 sentences with exact numbers)
2. Most critical issue or opportunity
3. 2-3 specific actions
"""

        analysis, tokens = self._call_llm(prompt, max_tokens=500)

        # Extract key metrics for coordinator
        rec_report = generate_recommendations(
            intent="revenue",
            db=db,
            platform=platform,
            time_period=time_period,
        )

        critical_recs = [
            r.action for r in rec_report.recommendations
            if r.severity == "CRITICAL"
        ][:3]

        return AgentResult(
            agent_name=self.name,
            role=self.role,
            analysis=analysis,
            recommendations=critical_recs,
            key_metrics={
                "forecast_period": forecast.get("next_period", "N/A"),
                "rules_triggered": len(rec_report.recommendations),
                "critical_alerts": sum(
                    1 for r in rec_report.recommendations
                    if r.severity == "CRITICAL"
                ),
            },
            confidence="high" if revenue_data else "low",
            tokens_used=tokens,
            elapsed_ms=0,
        )