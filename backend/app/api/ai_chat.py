"""
AI Chat Endpoint — Phase 3 update.
Now passes DB session to orchestrator for real KPI fetching.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.db.database import get_db
from app.ai.orchestrator import orchestrate
from app.schemas.responses import APIResponse

logger = logging.getLogger("sma_api.ai_chat")

router = APIRouter(prefix="/ai", tags=["AI Analytics"])


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="The user's analytics question",
        examples=["Why did Instagram ROI drop last month?"],
    )


@router.post("/chat", response_model=APIResponse)
def ai_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),       # ← DB injected here
):
    """
    Conversational AI analytics endpoint.
    Detects intent → fetches real KPIs → returns data-grounded answer.
    """
    logger.info(f"Chat request: {request.message[:60]}...")

    try:
        result = orchestrate(message=request.message, db=db)

        return APIResponse(
            success=True,
            message="AI response generated successfully",
            data={
                "question":               request.message,
                "answer":                 result["answer"],
                "model":                  result["model"],
                "tokens_used":            result["tokens_used"],
                "intent":                 result["intent"],
                "platform_detected":      result["platform_detected"],
                "time_period_detected":   result["time_period_detected"],
                "confidence":             result["confidence"],
                "kpi_data_fetched":       result["kpi_data_fetched"],
                "recommendations_count":  result["recommendations_count"],
                "recommendation_summary": result["recommendation_summary"],
            },
        )
    
    except ValueError as e:
        logger.error(f"Config error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        logger.error(f"Orchestration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="AI service temporarily unavailable",
        )