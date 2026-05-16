"""
Central configuration — reads from .env file.
All settings live here. Never hardcode credentials anywhere else.
"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "social_media_analytics"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""

    # App
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    API_VERSION: str = "v1"
    APP_TITLE: str = "Social Media Analytics API"
    APP_DESCRIPTION: str = (
        "Analytics API for Multi-Platform Ad Campaign Intelligence"
    )

    # ── AI Layer ──────────────────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = Path(__file__).resolve().parents[3] / ".env"
        extra = "allow"


settings = Settings()