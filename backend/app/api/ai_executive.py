"""
Executive AI Endpoints — Phase 5.

Two endpoints:
- GET /api/v1/ai/executive-summary  → AI-generated board briefing
- GET /api/v1/ai/smart-alerts       → Rule-based alerts, zero LLM cost
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.ai.executive_summary import generate_executive_summary
from app.ai.smart_alerts import scan_all_alerts
from app.schemas.responses import APIResponse

logger = logging.getLogger("sma_api.ai_executive")

router = APIRouter(prefix="/ai", tags=["AI Executive"])


@router.get("/executive-summary", response_model=APIResponse)
def executive_summary(db: Session = Depends(get_db)):
    """
    Generate a board-ready AI executive summary.
    Analyzes all platforms simultaneously.
    Includes KPI comparison, alerts, and strategic recommendations.
    """
    logger.info("Executive summary requested")

    try:
        result = generate_executive_summary(db)

        return APIResponse(
            success=True,
            message="Executive summary generated successfully",
            data=result,
        )

    except Exception as e:
        logger.error(f"Executive summary error: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="Executive summary service temporarily unavailable",
        )


@router.get("/smart-alerts", response_model=APIResponse)
def smart_alerts(db: Session = Depends(get_db)):
    """
    Scan all platforms for KPI threshold violations.
    Returns prioritized alert list — NO LLM cost.
    Fast enough to poll every few minutes from a dashboard.
    """
    logger.info("Smart alerts scan requested")

    try:
        report = scan_all_alerts(db)

        return APIResponse(
            success=True,
            message=f"Alert scan complete — {report.total_alerts if hasattr(report, 'total_alerts') else len(report.alerts)} alerts found",
            data=report.to_dict(),
        )

    except Exception as e:
        logger.error(f"Smart alerts error: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="Alert scanning service temporarily unavailable",
        )