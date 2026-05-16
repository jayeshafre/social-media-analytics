"""
AI Chat Endpoint — Phase 7 update.
Now accepts optional session_id for conversation continuity.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from app.db.database import get_db
from app.ai.orchestrator import orchestrate
from app.ai.memory.conversation import (
    get_session_info,
    clear_history,
    generate_session_id,
)
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
    session_id: Optional[str] = Field(
        default=None,
        description=(
            "Session ID for conversation continuity. "
            "Omit to start a new conversation. "
            "Reuse the same ID to continue an existing one."
        ),
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Why did Instagram ROI drop last month?",
                    "session_id": None
                }
            ]
        }
    }


@router.post("/chat", response_model=APIResponse)
def ai_chat(
    request: ChatRequest,
    db:      Session = Depends(get_db),
):
    """
    Conversational AI analytics endpoint with memory.

    - First message: omit session_id → system creates one
    - Follow-up messages: include the session_id from the first response
    - Session expires after 1 hour of inactivity
    """
    logger.info(
        f"Chat request | session={request.session_id or 'NEW'} | "
        f"message={request.message[:60]}..."
    )

    try:
        result = orchestrate(
            message=request.message,
            db=db,
            session_id=request.session_id,
        )

        return APIResponse(
            success=True,
            message="AI response generated successfully",
            data={
                "question":               request.message,
                "answer":                 result["answer"],
                "model":                  result["model"],
                "tokens_used":            result["tokens_used"],
                "session_id":             result["session_id"],
                "intent":                 result["intent"],
                "platform_detected":      result["platform_detected"],
                "time_period_detected":   result["time_period_detected"],
                "confidence":             result["confidence"],
                "kpi_data_fetched":       result["kpi_data_fetched"],
                "rag_context_retrieved":  result["rag_context_retrieved"],
                "recommendations_count":  result["recommendations_count"],
                "recommendation_summary": result["recommendation_summary"],
                "conversation_length":    result["conversation_length"],
                "memory_saved":           result["memory_saved"],
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


@router.get("/session/{session_id}", response_model=APIResponse)
def get_session(session_id: str):
    """
    Get metadata about an existing conversation session.
    Use this to check if a session is still active.
    """
    info = get_session_info(session_id)
    return APIResponse(
        success=True,
        message="Session info retrieved",
        data=info,
    )


@router.delete("/session/{session_id}", response_model=APIResponse)
def clear_session(session_id: str):
    """
    Clear conversation history for a session.
    Use this when the user wants to start fresh.
    """
    cleared = clear_history(session_id)
    return APIResponse(
        success=True,
        message="Session cleared" if cleared else "Session not found or Redis unavailable",
        data={"session_id": session_id, "cleared": cleared},
    )


@router.post("/session/new", response_model=APIResponse)
def new_session():
    """
    Generate a new session ID without sending a message.
    Useful for pre-creating sessions on frontend load.
    """
    session_id = generate_session_id()
    return APIResponse(
        success=True,
        message="New session created",
        data={"session_id": session_id},
    )