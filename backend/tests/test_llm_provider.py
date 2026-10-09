"""Tests for provider resolution + settings — no network access ever."""

import pytest

from app.config import get_settings
from app.llm import host_of, resolve_provider_config


def test_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        resolve_provider_config("claude")


def test_gemini_requires_key():
    config = resolve_provider_config("gemini")
    assert config.requires_key is True
    assert config.key_setting == "gemini_api_key"
    assert config.default_model == "gemini-2.5-flash"


def test_ollama_needs_no_key():
    config = resolve_provider_config("ollama")
    assert config.requires_key is False
    assert "localhost" in config.base_url


def test_groq_default_model():
    assert resolve_provider_config("groq").default_model == "llama-3.3-70b-versatile"


def test_host_of_extracts_netloc():
    assert host_of("https://api.groq.com/openai/v1") == "api.groq.com"


def test_settings_defaults():
    settings = get_settings()
    assert settings.llm_provider in ("gemini", "groq", "ollama")
    assert settings.database_url.startswith("sqlite+aiosqlite")
