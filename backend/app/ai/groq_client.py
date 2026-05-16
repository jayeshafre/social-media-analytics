"""
Groq API client — single instance shared across the app.
Same pattern as SQLAlchemy engine in database.py:
create once, reuse everywhere.
"""

import logging
from groq import Groq
from app.core.config import settings

logger = logging.getLogger("sma_api.groq")


def get_groq_client() -> Groq:
    """
    Returns a configured Groq client.
    Raises clearly if API key is missing — 
    so you know immediately what went wrong.
    """
    if not settings.GROQ_API_KEY:
        logger.error("GROQ_API_KEY is not set in environment")
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to your .env file."
        )

    return Groq(api_key=settings.GROQ_API_KEY)


# Single shared instance — imported by services
groq_client = get_groq_client()