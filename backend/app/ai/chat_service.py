"""
AI Chat Service — Phase 2 update.

Now accepts an optional system_prompt override.
The orchestrator injects domain-specific context through this.
"""

import logging
from app.ai.groq_client import groq_client
from app.core.config import settings

logger = logging.getLogger("sma_api.chat_service")

BASE_SYSTEM_PROMPT = """
You are an expert AI Marketing Analytics Assistant built for 
a multi-platform social media analytics platform.

You analyze performance data across:
Instagram, Facebook, YouTube, LinkedIn, and WhatsApp.

You must:
- Always be precise and data-driven in your reasoning
- Explain metrics in terms a marketing manager can understand
- Never make up numbers — only explain what data shows
- Keep responses focused, structured, and professional
- When context is provided, use it to shape your answer domain

You are NOT a general chatbot.
You are a specialized marketing intelligence assistant.
"""


def get_ai_response(
    user_message: str,
    system_prompt: str = BASE_SYSTEM_PROMPT,
) -> dict:
    """
    Send a message to Groq and return structured response.

    Args:
        user_message:  The question (may include injected context)
        system_prompt: Override system prompt (orchestrator injects domain context)

    Returns:
        dict with answer, model, tokens_used
    """
    logger.info(f"AI request: {user_message[:80]}...")

    try:
        completion = groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            temperature=0.3,
            max_tokens=1024,
        )

        answer = completion.choices[0].message.content
        model_used = completion.model

        logger.info(
            f"Response generated | model={model_used} | "
            f"tokens={completion.usage.total_tokens}"
        )

        return {
            "answer": answer,
            "model": model_used,
            "tokens_used": completion.usage.total_tokens,
        }

    except Exception as e:
        logger.error(f"Groq API error: {e}", exc_info=True)
        raise