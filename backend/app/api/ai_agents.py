"""
Multi-Agent AI Endpoint — Phase 9.

POST /api/v1/ai/agents/analyze
→ Activates specialist agents based on intent
→ Coordinator synthesizes unified answer
→ Returns rich metadata about agent collaboration
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from app.db.database import get_db
from app.ai.intent_detector import detect_intent
from app.ai.memory.conversation import save_exchange, generate_session_id
from app.agents.agent_router import run_agents
from app.schemas.responses import APIResponse

logger = logging.getLogger("sma_api.ai_agents")

router = APIRouter(prefix="/ai/agents", tags=["Multi-Agent AI"])


class AgentRequest(BaseModel):
    message:    str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Complex analytics question for multi-agent analysis",
        examples=["Why is our overall marketing performance declining?"],
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for conversation continuity",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "message": "Why is our overall marketing performance declining?",
                "session_id": None,
            }]
        }
    }


@router.post("/analyze", response_model=APIResponse)
def agent_analyze(
    request: AgentRequest,
    db:      Session = Depends(get_db),
):
    """
    Multi-agent analysis endpoint.

    Activates specialist agents based on question intent.
    Each agent independently analyzes its domain.
    Coordinator synthesizes all findings into unified answer.

    Best for complex, cross-domain questions like:
    - 'Why is overall performance declining?'
    - 'Which platform should we increase budget on?'
    - 'What is causing our conversion rate issues?'
    """
    session_id = request.session_id or generate_session_id()

    logger.info(
        f"Agent analysis | session={session_id} | "
        f"message={request.message[:60]}..."
    )

    try:
        # Detect intent for routing
        intent = detect_intent(request.message)

        logger.info(
            f"Intent detected | intent={intent.intent} | "
            f"platform={intent.platform}"
        )

        # Run agent system
        result = run_agents(
            message=request.message,
            intent=intent.intent,
            db=db,
            platform=intent.platform,
            time_period=intent.time_period,
            session_id=session_id,
        )

        # Save to conversation memory
        save_exchange(
            session_id=session_id,
            user_message=request.message,
            assistant_message=result["answer"],
        )

        return APIResponse(
            success=True,
            message=(
                f"Multi-agent analysis complete — "
                f"{result['agents_activated']} agents activated"
            ),
            data={
                "question":          request.message,
                "answer":            result["answer"],
                "session_id":        session_id,
                "intent":            intent.intent,
                "platform_detected": intent.platform,
                "agents_activated":  result["agents_activated"],
                "agents_used":       result["agents_list"],
                "total_tokens":      result["total_tokens"],
                "elapsed_ms":        result["elapsed_ms"],
                "agent_details":     result["agent_details"],
            },
        )

    except Exception as e:
        logger.error(f"Agent analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="Multi-agent system temporarily unavailable",
        )