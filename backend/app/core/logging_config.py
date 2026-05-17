"""
Structured JSON Logging — Phase 10.

Production logging outputs JSON instead of plain text.
This makes logs parseable by monitoring tools like:
- Datadog, Grafana, CloudWatch, ELK Stack

Development: human-readable colored output
Production:  machine-readable JSON output

Controlled by APP_ENV environment variable.
"""

import logging
import json
import time
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """
    Formats log records as JSON for production monitoring.

    Output example:
    {
      "timestamp": "2024-12-01T10:30:00Z",
      "level": "INFO",
      "logger": "sma_api.chat_service",
      "message": "AI response generated",
      "service": "social-media-analytics-ai"
    }
    """

    SERVICE_NAME = "social-media-analytics-ai"

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level":     record.levelname,
            "logger":    record.name,
            "message":   record.getMessage(),
            "service":   self.SERVICE_NAME,
        }

        # Include exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Include extra fields if present
        for key in ["request_id", "session_id", "user_ip", "endpoint"]:
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)

        return json.dumps(log_entry)


def configure_logging(app_env: str = "development") -> None:
    """
    Configure logging based on environment.

    Development: Standard readable format
    Production:  JSON format for log aggregation
    """
    if app_env == "production":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Root logger
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(
        logging.DEBUG if app_env == "development" else logging.INFO
    )

    # Silence noisy third-party loggers in production
    if app_env == "production":
        for noisy in [
            "uvicorn.access",
            "sentence_transformers",
            "chromadb",
            "httpx",
        ]:
            logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger("sma_api").info(
        f"Logging configured | env={app_env} | "
        f"format={'JSON' if app_env == 'production' else 'TEXT'}"
    )