from __future__ import annotations

import os
from typing import Optional
from pydantic import BaseModel


class Settings(BaseModel):
    secret_key: str
    openai_api_key: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None
    huggingface_api_token: Optional[str] = None
    database_url: Optional[str] = None
    sentry_dsn: Optional[str] = None


def load_settings() -> Settings:
    # Do NOT read from config files; only environment variables.
    secret = os.getenv("EVAL_SERVER_SECRET_KEY")
    if not secret:
        raise RuntimeError("Missing required environment variable: EVAL_SERVER_SECRET_KEY")
    return Settings(
        secret_key=secret,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        google_ai_api_key=os.getenv("GOOGLE_AI_API_KEY"),
        huggingface_api_token=os.getenv("HUGGINGFACE_API_TOKEN"),
        database_url=os.getenv("DATABASE_URL"),
        sentry_dsn=os.getenv("SENTRY_DSN"),
    )


__all__ = ["Settings", "load_settings"]
