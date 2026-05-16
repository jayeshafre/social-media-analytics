"""
ML Context Builder — Phase 8.

Decides when to run ML models and formats their output
for injection into the AI prompt.

Design principle:
ML context is injected selectively — only when relevant.
We do not run forecasting on every single request.
This keeps response times fast and token costs low.

When ML runs:
- revenue intent    → forecast revenue + anomaly check
- anomaly intent    → anomaly detection (primary) + forecast
- platform intent   → forecast per platform
- campaign intent   → forecast CTR and conversion rate
- general intent    → no ML (not needed)
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.ml.forecaster import generate_forecasts
from app.ml.anomaly_detector import detect_anomalies

logger = logging.getLogger("sma_api.ml_context_builder")


def build_ml_context(
    intent:   str,
    db:       Session,
    platform: Optional[str] = None,
) -> str:
    """
    Build ML context for prompt injection based on intent.

    Args:
        intent:   Detected intent category
        db:       SQLAlchemy session
        platform: Detected platform filter

    Returns:
        Formatted ML context string for prompt injection.
        Empty string if ML not relevant for this intent.
    """
    logger.info(
        f"Building ML context | intent={intent} | platform={platform}"
    )

    ml_parts = []

    try:
        if intent == "anomaly":
            # Primary: anomaly detection
            # Secondary: forecast to show where things are heading
            anomaly_result = detect_anomalies(
                db=db,
                platform=platform,
            )
            if anomaly_result["status"] == "success":
                ml_parts.append(anomaly_result["formatted"])

            forecast_result = generate_forecasts(
                db=db,
                platform=platform,
            )
            if forecast_result["status"] == "success":
                ml_parts.append(forecast_result["formatted"])

        elif intent == "revenue":
            # Forecast revenue and ROI
            forecast_result = generate_forecasts(
                db=db,
                platform=platform,
            )
            if forecast_result["status"] == "success":
                ml_parts.append(forecast_result["formatted"])

            # Also check for anomalies in revenue
            anomaly_result = detect_anomalies(
                db=db,
                platform=platform,
                top_n_anomalies=3,
            )
            if anomaly_result["status"] == "success":
                ml_parts.append(anomaly_result["formatted"])

        elif intent == "platform":
            # Forecast for the specific platform or all
            forecast_result = generate_forecasts(
                db=db,
                platform=platform,
            )
            if forecast_result["status"] == "success":
                ml_parts.append(forecast_result["formatted"])

        elif intent == "campaign":
            # Forecast campaign-relevant KPIs
            forecast_result = generate_forecasts(
                db=db,
                platform=platform,
            )
            if forecast_result["status"] == "success":
                # Only include CTR, conversion rate, ROAS lines
                lines = forecast_result["formatted"].split("\n")
                relevant = [
                    l for l in lines
                    if any(kpi in l for kpi in
                           ["CTR", "Conversion Rate", "ROAS", "ML FORECAST"])
                ]
                if relevant:
                    ml_parts.append("\n".join(relevant))

        # General and engagement intents — skip ML
        # Not enough signal to make ML useful here

    except Exception as e:
        logger.error(f"ML context build error: {e}", exc_info=True)
        return ""

    if not ml_parts:
        return ""

    return "\n\n".join(ml_parts)