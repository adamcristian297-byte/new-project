"""FastAPI application factory — minimal Phase 0 skeleton.

Health endpoint echoes the active LLM provider and model (spec section 2.3)
without leaking any key material. The deterministic risk engine, parsing and
trading services arrive in later phases under /api/v1 (spec section 8).
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import get_settings
from app.llm import (
    host_of,
    resolve_provider_config,
)

app = FastAPI(
    title="StockPilot API",
    version=__version__,
    description="AI-parsed strategy trading platform — paper trading by default.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, Any]:
    """Liveness + active LLM provider echo. Never exposes key material."""
    settings = get_settings()
    try:
        config = resolve_provider_config(settings.llm_provider)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    key_state = "unset"
    if config.requires_key:
        api_key = getattr(settings, config.key_setting)
        key_state = "set" if api_key else "unset"
    return {
        "status": "ok",
        "version": __version__,
        "llm": {
            "provider": config.name,
            "model": settings.llm_model or config.default_model,
            "base_url_host": host_of(config.base_url),
            "key_state": key_state,
        },
    }
