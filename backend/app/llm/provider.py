"""LLM provider registry (spec section 2.3).

All three free providers expose OpenAI-compatible endpoints, so a single
`openai` client library works with a swappable base URL.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    base_url: str
    default_model: str
    requires_key: bool
    key_setting: str  # Settings attribute holding the API key


PROVIDERS: dict[str, ProviderConfig] = {
    "gemini": ProviderConfig(
        name="gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        default_model="gemini-2.5-flash",
        requires_key=True,
        key_setting="gemini_api_key",
    ),
    "groq": ProviderConfig(
        name="groq",
        base_url="https://api.groq.com/openai/v1",
        default_model="llama-3.3-70b-versatile",
        requires_key=True,
        key_setting="groq_api_key",
    ),
    "ollama": ProviderConfig(
        name="ollama",
        base_url="http://localhost:11434/v1",
        default_model="qwen2.5:7b",
        requires_key=False,
        key_setting="",
    ),
}


def resolve_provider_config(provider: str) -> ProviderConfig:
    """Return the provider config or raise ValueError for unknown providers."""
    try:
        return PROVIDERS[provider]
    except KeyError:
        known = ", ".join(sorted(PROVIDERS))
        raise ValueError(f"Unknown LLM provider {provider!r}. Known: {known}") from None


def host_of(url: str) -> str:
    """Public-safe host label for health output (never logs keys)."""
    return urlparse(url).netloc or url
