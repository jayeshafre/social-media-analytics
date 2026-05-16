"""
Intent Detector — Phase 2.

Classifies user questions into known analytics domains.

Layer 1: Rule-based keyword matching (instant, free)
Layer 2: LLM fallback for ambiguous questions (used rarely)

Intent categories:
- revenue       → ROI, ROAS, profit, revenue, spend
- campaign      → campaign, objective, influencer, CTR, CPC
- audience      → audience, age, demographic, customer segment
- platform      → Instagram, Facebook, YouTube, LinkedIn, WhatsApp
- engagement    → engagement, likes, shares, comments, reach
- anomaly       → drop, spike, sudden, unexpected, why did
- general       → anything that doesn't match above
"""

import re
import logging
from dataclasses import dataclass
from typing import Optional
from app.ai.groq_client import groq_client
from app.core.config import settings

logger = logging.getLogger("sma_api.intent_detector")


# ─────────────────────────────────────────
# Intent result — structured output
# dataclass = lightweight, no DB needed
# ─────────────────────────────────────────
@dataclass
class IntentResult:
    intent: str              # primary intent category
    platform: Optional[str]  # detected platform if mentioned
    time_period: Optional[str]  # detected time reference
    confidence: str          # "high" (rules) or "medium" (llm)
    raw_message: str         # original user message


# ─────────────────────────────────────────
# Keyword maps — rule-based layer
# ─────────────────────────────────────────
INTENT_KEYWORDS = {
    "revenue": [
        "revenue", "roi", "roas", "profit", "spend", "return",
        "cost", "cac", "customer acquisition", "refund", "loss",
        "earning", "income", "budget", "financial"
    ],
    "campaign": [
        "campaign", "objective", "influencer", "ctr", "cpc",
        "click", "impression", "conversion rate", "performance",
        "ad type", "campaign type", "best campaign", "worst campaign"
    ],
    "audience": [
        "audience", "age", "demographic", "segment", "customer",
        "gender", "group", "target", "who is", "buyer", "user base"
    ],
    "platform": [
        "instagram", "facebook", "youtube", "linkedin", "whatsapp",
        "platform", "channel", "compare platform", "which platform"
    ],
    "engagement": [
        "engagement", "likes", "shares", "comments", "reach",
        "sentiment", "interaction", "response", "organic", "viral"
    ],
    "anomaly": [
        "drop", "spike", "sudden", "unexpected", "why did",
        "what happened", "decline", "fall", "increase sharply",
        "anomaly", "unusual", "abnormal", "changed"
    ],
}

PLATFORM_KEYWORDS = {
    "instagram": "Instagram",
    "facebook": "Facebook",
    "youtube": "YouTube",
    "linkedin": "LinkedIn",
    "whatsapp": "WhatsApp",
}

TIME_KEYWORDS = {
    "last month": "last_month",
    "this month": "this_month",
    "last quarter": "last_quarter",
    "this quarter": "this_quarter",
    "last year": "last_year",
    "this year": "this_year",
    "yesterday": "yesterday",
    "last week": "last_week",
}


# ─────────────────────────────────────────
# Rule-based detection — Layer 1
# ─────────────────────────────────────────
def _detect_by_rules(message: str) -> Optional[str]:
    """
    Check message against keyword maps.
    Returns intent name if confident match found, else None.
    """
    message_lower = message.lower()
    scores = {}

    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in message_lower)
        if score > 0:
            scores[intent] = score

    if not scores:
        return None

    # Return the intent with the highest keyword match count
    return max(scores, key=scores.get)


def _detect_platform(message: str) -> Optional[str]:
    """Extract platform name if mentioned in message."""
    message_lower = message.lower()
    for keyword, platform in PLATFORM_KEYWORDS.items():
        if keyword in message_lower:
            return platform
    return None


def _detect_time_period(message: str) -> Optional[str]:
    """Extract time reference if mentioned in message."""
    message_lower = message.lower()
    for phrase, code in TIME_KEYWORDS.items():
        if phrase in message_lower:
            return code
    return None


# ─────────────────────────────────────────
# LLM fallback — Layer 2
# Only called when rules return no match
# ─────────────────────────────────────────
def _detect_by_llm(message: str) -> str:
    """
    Ask Groq to classify the intent when rules fail.
    Forces a single-word response to keep it deterministic.
    """
    logger.info("Rules failed — falling back to LLM intent detection")

    prompt = f"""
You are an intent classifier for a marketing analytics platform.

Classify this user message into EXACTLY ONE of these categories:
- revenue
- campaign  
- audience
- platform
- engagement
- anomaly
- general

User message: "{message}"

Respond with ONLY the category name. No explanation. No punctuation.
"""
    try:
        completion = groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,   # Zero temperature = fully deterministic
            max_tokens=10,     # We only need one word back
        )
        raw = completion.choices[0].message.content.strip().lower()

        # Validate it returned a known intent
        known = set(INTENT_KEYWORDS.keys()) | {"general"}
        detected = raw if raw in known else "general"

        logger.info(f"LLM detected intent: {detected}")
        return detected

    except Exception as e:
        logger.error(f"LLM intent detection failed: {e}")
        return "general"


# ─────────────────────────────────────────
# Main public function
# ─────────────────────────────────────────
def detect_intent(message: str) -> IntentResult:
    """
    Classify user message into an IntentResult.

    Process:
    1. Try rule-based detection first (fast, free)
    2. If no match, fall back to LLM classification
    3. Always extract platform and time period separately
    """
    logger.info(f"Detecting intent for: {message[:60]}...")

    # Layer 1
    intent = _detect_by_rules(message)
    confidence = "high"

    # Layer 2 fallback
    if intent is None:
        intent = _detect_by_llm(message)
        confidence = "medium"

    platform = _detect_platform(message)
    time_period = _detect_time_period(message)

    result = IntentResult(
        intent=intent,
        platform=platform,
        time_period=time_period,
        confidence=confidence,
        raw_message=message,
    )

    logger.info(
        f"Intent detected → intent={intent} | platform={platform} | "
        f"time={time_period} | confidence={confidence}"
    )

    return result