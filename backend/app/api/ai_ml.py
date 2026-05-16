"""
ML Endpoints — Phase 8.

Endpoints:
- GET /api/v1/ai/ml/forecast        → KPI forecasts for next month
- GET /api/v1/ai/ml/anomalies       → Statistical anomaly detection
- GET /api/v1/ai/ml/full-analysis   → Forecast + anomalies combined
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.ml.forecaster import generate_forecasts
from app.ml.anomaly_detector import detect_anomalies
from app.schemas.responses import APIResponse

logger = logging.getLogger("sma_api.ai_ml")

router = APIRouter(prefix="/ai/ml", tags=["ML Analytics"])


@router.get("/forecast", response_model=APIResponse)
def get_forecast(
    platform: Optional[str] = Query(
        default=None,
        description="Filter by platform (Instagram, Facebook, etc.)",
    ),
    db: Session = Depends(get_db),
):
    """
    Generate ML-powered KPI forecasts for next month.
    Uses Linear Regression trained on your full historical data.
    """
    logger.info(f"Forecast requested | platform={platform}")

    try:
        result = generate_forecasts(db=db, platform=platform)

        return APIResponse(
            success=True,
            message="ML forecasts generated successfully",
            data=result,
        )

    except Exception as e:
        logger.error(f"Forecast error: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="Forecasting service temporarily unavailable",
        )


@router.get("/anomalies", response_model=APIResponse)
def get_anomalies(
    platform: Optional[str] = Query(
        default=None,
        description="Filter by platform",
    ),
    top_n: int = Query(
        default=5,
        ge=1,
        le=20,
        description="Number of top anomalies to return",
    ),
    db: Session = Depends(get_db),
):
    """
    Detect statistically anomalous months using Isolation Forest.
    Returns months where KPI patterns deviated significantly from normal.
    """
    logger.info(f"Anomaly detection requested | platform={platform}")

    try:
        result = detect_anomalies(
            db=db,
            platform=platform,
            top_n_anomalies=top_n,
        )

        return APIResponse(
            success=True,
            message="Anomaly detection complete",
            data=result,
        )

    except Exception as e:
        logger.error(f"Anomaly detection error: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="Anomaly detection service temporarily unavailable",
        )


@router.get("/full-analysis", response_model=APIResponse)
def get_full_ml_analysis(
    platform: Optional[str] = Query(default=None),
    db:       Session = Depends(get_db),
):
    """
    Combined ML analysis: forecasts + anomaly detection.
    Most comprehensive ML view of platform performance.
    """
    logger.info(f"Full ML analysis requested | platform={platform}")

    try:
        forecasts = generate_forecasts(db=db, platform=platform)
        anomalies = detect_anomalies(db=db, platform=platform)

        return APIResponse(
            success=True,
            message="Full ML analysis complete",
            data={
                "forecasts": forecasts,
                "anomalies": anomalies,
            },
        )

    except Exception as e:
        logger.error(f"Full ML analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="ML analysis service temporarily unavailable",
        )