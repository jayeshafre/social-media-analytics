"""
Keyword Explainer — Post-Phase 10 Enhancement.

Scans AI responses for marketing/analytics jargon
and returns beginner-friendly explanations for every
term found.

Design:
- Definitions are hardcoded (deterministic, zero LLM cost)
- Case-insensitive matching
- Only returns terms actually found in the response
- Ordered by first appearance in the text
- Plugs into chat_service.py as a post-processing step
"""

import re
import logging
from typing import Optional

logger = logging.getLogger("sma_api.keyword_explainer")

# ─────────────────────────────────────────────────────────────
# Master glossary
# Key   = canonical term (used for matching)
# Value = beginner-friendly one-line explanation
# ─────────────────────────────────────────────────────────────
GLOSSARY: dict[str, str] = {

    # ── Core KPIs ─────────────────────────────────────────────
    "ROI": (
        "Return on Investment — how much profit you made compared "
        "to what you spent. ROI of 200% means you doubled your money."
    ),
    "ROAS": (
        "Return on Ad Spend — revenue earned for every ₹1 spent on ads. "
        "ROAS of 4x means ₹4 earned per ₹1 spent."
    ),
    "CTR": (
        "Click-Through Rate — percentage of people who saw your ad "
        "and clicked on it. Higher CTR = more compelling ad creative."
    ),
    "CPC": (
        "Cost Per Click — how much you paid for each click on your ad. "
        "Lower CPC = more efficient traffic acquisition."
    ),
    "CPM": (
        "Cost Per Mille — cost per 1,000 ad impressions. "
        "Used to measure brand awareness campaign efficiency."
    ),
    "CAC": (
        "Customer Acquisition Cost — total cost to acquire one new customer. "
        "CAC must be lower than what that customer is worth (LTV)."
    ),
    "LTV": (
        "Lifetime Value — total revenue a customer generates "
        "over their entire relationship with your business."
    ),
    "CVR": (
        "Conversion Rate — percentage of clicks that resulted "
        "in a purchase or lead. Industry average is 2-5%."
    ),

    # ── Analytics Terms ───────────────────────────────────────
    "conversion rate": (
        "Percentage of ad clicks that turned into actual purchases or leads. "
        "2-5% is considered healthy in most industries."
    ),
    "impressions": (
        "Total number of times your ad was displayed to users, "
        "regardless of whether they clicked."
    ),
    "engagement rate": (
        "Percentage of people who interacted with your ad "
        "(liked, commented, shared, or saved it)."
    ),
    "sentiment score": (
        "A number between -1 and +1 measuring audience mood toward your ads. "
        "Positive = good reactions. Negative = complaints or criticism."
    ),
    "bounce rate": (
        "Percentage of visitors who clicked your ad but left "
        "without taking any action. High bounce rate = landing page problem."
    ),
    "funnel": (
        "The journey from seeing an ad → clicking it → buying. "
        "Each step loses some people — optimizing the funnel improves results."
    ),
    "attribution": (
        "Method of deciding which ad gets credit for a sale "
        "when a customer saw multiple ads before buying."
    ),
    "lookalike audience": (
        "A new audience that Facebook/Instagram finds based on your "
        "best existing customers — people who behave similarly."
    ),
    "retargeting": (
        "Showing ads to people who already visited your website or "
        "engaged with your content but did not buy yet."
    ),
    "frequency": (
        "Average number of times the same person saw your ad. "
        "High frequency (>3) causes ad fatigue and declining performance."
    ),
    "ad fatigue": (
        "When your audience has seen the same ad too many times "
        "and stops responding to it. Fix: rotate creatives regularly."
    ),
    "creative": (
        "The actual ad content — the image, video, copy, and "
        "call-to-action that your audience sees."
    ),

    # ── ML / AI Terms ─────────────────────────────────────────
    "anomaly": (
        "A data point that is statistically very different from normal. "
        "Could be an unusually good month or a sudden performance crash."
    ),
    "anomalies": (
        "Months or periods where performance was statistically unusual — "
        "either much better or much worse than the historical average."
    ),
    "anomaly detection": (
        "A machine learning technique that automatically finds months "
        "where performance deviated significantly from normal patterns."
    ),
    "isolation forest": (
        "A machine learning algorithm used to find anomalies. "
        "It isolates unusual data points by randomly partitioning data."
    ),
    "forecast": (
        "A prediction of future performance based on historical trends. "
        "Our system uses 6 years of your data to predict next month."
    ),
    "linear regression": (
        "A mathematical model that finds the trend in your historical data "
        "and extends it to predict future values."
    ),
    "baseline": (
        "The average normal performance level used as a reference point. "
        "Anomalies are periods that deviate significantly from the baseline."
    ),
    "confidence": (
        "How reliable a prediction or analysis is. "
        "High = strong historical pattern. Low = limited data available."
    ),
    "r2 score": (
        "A measure of how well the forecasting model fits your data. "
        "Ranges from 0 to 1. Above 0.7 = good fit."
    ),

    # ── Platform Terms ────────────────────────────────────────
    "benchmark": (
        "The industry average performance standard. "
        "Comparing your numbers to the benchmark shows if you are "
        "above or below what similar businesses achieve."
    ),
    "market benchmark": (
        "The average CTR or CPC that all advertisers on a platform "
        "typically achieve. Beating it means your ads outperform the market."
    ),
    "b2b": (
        "Business-to-Business — selling products or services to "
        "other businesses rather than individual consumers."
    ),
    "d2c": (
        "Direct-to-Consumer — selling directly to end customers "
        "without going through retailers or middlemen."
    ),
    "cta": (
        "Call-To-Action — the button or phrase that tells the viewer "
        "what to do next (e.g. 'Shop Now', 'Learn More', 'Sign Up')."
    ),

    # ── Campaign Terms ────────────────────────────────────────
    "campaign objective": (
        "The goal you set for a campaign — such as Sales, Traffic, "
        "Brand Awareness, or Lead Generation."
    ),
    "campaign stage": (
        "Where the campaign is in its lifecycle — "
        "Awareness (top), Consideration (middle), or Conversion (bottom)."
    ),
    "influencer": (
        "A social media personality who promotes your products "
        "to their followers. Influencer campaigns often boost engagement."
    ),
    "organic reach": (
        "People who saw your content without you paying for it — "
        "through shares, follows, or platform algorithms."
    ),
    "paid reach": (
        "People who saw your content because you paid for "
        "advertising to show it to them."
    ),

    # ── Financial Terms ───────────────────────────────────────
    "ad spend": (
        "The total amount of money spent on running advertisements "
        "across all platforms."
    ),
    "profit margin": (
        "Percentage of revenue that is actual profit after all costs. "
        "Higher margin = more money kept per sale."
    ),
    "refund rate": (
        "Percentage of sales that were returned and refunded. "
        "High refund rate reduces actual profit significantly."
    ),

    # ── RAG / System Terms ────────────────────────────────────
    "rag": (
        "Retrieval Augmented Generation — a technique where the AI "
        "searches your own documents before answering, "
        "making responses more accurate and relevant."
    ),
    "semantic search": (
        "Search that understands the meaning of your question — "
        "not just exact keywords. Finds relevant content even if "
        "it uses different words."
    ),
    "vector": (
        "A list of numbers that represents the meaning of a piece "
        "of text. Similar meanings = similar numbers."
    ),
}

# Build a lowercase lookup for fast matching
_GLOSSARY_LOWER: dict[str, tuple[str, str]] = {
    k.lower(): (k, v) for k, v in GLOSSARY.items()
}


def extract_terms(text: str) -> list[dict]:
    """
    Scan response text for known glossary terms.
    Returns list of {term, explanation} dicts
    in order of first appearance.

    Args:
        text: The AI response text to scan

    Returns:
        List of matched terms with explanations,
        ordered by first appearance, deduplicated.
    """
    text_lower    = text.lower()
    found         = {}   # term_lower → (canonical, explanation, position)

    for term_lower, (canonical, explanation) in _GLOSSARY_LOWER.items():
        # Use word boundary matching for short terms (CTR, ROI etc.)
        # Use simple substring for longer phrases
        if len(term_lower) <= 5:
            pattern = rf'\b{re.escape(term_lower)}\b'
        else:
            pattern = re.escape(term_lower)

        match = re.search(pattern, text_lower)
        if match and term_lower not in found:
            found[term_lower] = (
                canonical,
                explanation,
                match.start(),   # position for ordering
            )

    # Sort by position of first appearance in text
    sorted_terms = sorted(found.values(), key=lambda x: x[2])

    return [
        {"term": canonical, "explanation": explanation}
        for canonical, explanation, _ in sorted_terms
    ]


def build_terms_section(terms: list[dict]) -> Optional[str]:
    """
    Build a formatted 'Terms Explained' text block.
    Returns None if no terms found.
    """
    if not terms:
        return None

    lines = ["📚 Terms Explained:"]
    for item in terms:
        lines.append(f"• {item['term']}: {item['explanation']}")

    return "\n".join(lines)