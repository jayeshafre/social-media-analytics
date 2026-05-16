"""
AI Chat Service — Phase 7 update.

Now supports multi-turn conversation via messages[] history.
History is passed from the orchestrator after loading from Redis.

The messages[] list follows the OpenAI/Groq format:
[
  {"role": "system",    "content": "..."},
  {"role": "user",      "content": "first question"},
  {"role": "assistant", "content": "first answer"},
  {"role": "user",      "content": "follow-up question"},  ← current
]
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
- When conversation history is provided, maintain continuity
  and answer follow-up questions with full awareness of
  what was previously discussed

You are NOT a general chatbot.
You are a specialized marketing intelligence assistant
with memory of this conversation.
"""


def get_ai_response(
    user_message:  str,
    system_prompt: str = BASE_SYSTEM_PROMPT,
    history:       list[dict] = None,
) -> dict:
    """
    Send a message to Groq with optional conversation history.

    Args:
        user_message:  The current user question (may include injected context)
        system_prompt: System instructions (domain context injected here)
        history:       Previous {role, content} messages from Redis

    Returns:
        dict with answer, model, tokens_used
    """
    logger.info(f"AI request: {user_message[:80]}...")

    # Build messages list
    # Structure: system → history → current user message
    messages = [{"role": "system", "content": system_prompt}]

    # Inject conversation history between system and current message
    if history:
        # Only include the last 6 exchanges to manage token budget
        recent_history = history[-12:]  # 12 messages = 6 exchanges
        messages.extend(recent_history)
        logger.info(f"History injected | messages={len(recent_history)}")

    # Add the current enriched user message
    messages.append({"role": "user", "content": user_message})

    try:
        completion = groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )

        answer     = completion.choices[0].message.content
        model_used = completion.model

        logger.info(
            f"Response generated | model={model_used} | "
            f"tokens={completion.usage.total_tokens}"
        )

        return {
            "answer":      answer,
            "model":       model_used,
            "tokens_used": completion.usage.total_tokens,
        }

    except Exception as e:
        logger.error(f"Groq API error: {e}", exc_info=True)
        raise