"""Application settings (spec section 2.5).

Reads the repo-root `.env` file so there is exactly one env file for both
backend and future tooling. Real values are never committed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config.py -> parents[2] == repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT_ENV_FILE = REPO_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- LLM provider (spec section 2.3) ---
    llm_provider: Literal["gemini", "groq", "ollama"] = "gemini"
    gemini_api_key: str = ""
    groq_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434/v1"
    llm_model: str = ""  # empty -> provider default

    # --- Database ---
    database_url: str = "sqlite+aiosqlite:///./stockpilot.db"

    # --- Auth / crypto (populated in Phase 1+) ---
    jwt_secret: str = ""
    jwt_refresh_secret: str = ""
    encryption_key: str = ""

    # --- Optional notifications (free tiers) ---
    ntfy_topic: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # --- Optional live trading (Phase 6 only) ---
    alpaca_key: str = ""
    alpaca_secret: str = ""


def get_settings() -> Settings:
    return Settings()
