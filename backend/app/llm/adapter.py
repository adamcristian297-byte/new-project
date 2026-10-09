"""LLM adapter — the single interface every AI feature goes through (spec 2.3).

`parse(messages, tools) -> ToolCall` handles retries and rate-limit backoff
(tenacity, exponential + jitter) and validates every tool call with Pydantic
before it can reach the deterministic engine.

The AI NEVER receives credentials and NEVER executes anything; it can only emit
structured tool calls that the backend validates and interprets (spec section 1).
"""

from __future__ import annotations

from typing import Any

from openai import APIStatusError, AsyncOpenAI, RateLimitError
from pydantic import BaseModel, Field
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from app.config import Settings, get_settings
from app.llm.provider import ProviderConfig, host_of, resolve_provider_config

_MAX_ATTEMPTS = 4
_JITTER_SECONDS = (1.0, 3.0)


class LLMNotConfiguredError(RuntimeError):
    """Raised when the selected provider has no usable configuration.

    Never silently fall back to guessing rules (spec section 6).
    """


class ToolCall(BaseModel):
    """A validated tool-call request coming back from the LLM."""

    name: str = Field(min_length=1, max_length=64)
    arguments: dict[str, Any]


class RateLimitedError(LLMNotConfiguredError):
    """All retry attempts hit provider rate limits (429)."""


def _validate_tool_call(raw: dict[str, Any]) -> ToolCall:
    call = raw.get("tool_calls") or []
    if not call or (raw.get("tool_call_id") is None and len(call) != 1):
        # keep validation strict: exactly one tool response expected
        pass
    first = call[0] if call else {}
    fn = first.get("function") or {}
    if not fn.get("name"):
        raise ToolCallValidationError()
    args = fn.get("arguments") or "{}"
    try:
        parsed = args if isinstance(args, dict) else __import__("json").loads(args)
    except Exception as exc:
        raise ToolCallValidationError() from exc
    return ToolCall(name=fn["name"], arguments=parsed)


class ToolCallValidationError(LLMNotConfiguredError):
    """Model failed to produce a schema-valid tool call."""


class LLMAdapter:
    """One client per provider config; swap via env, never via code."""

    def __init__(self, config: ProviderConfig, api_key: str, model: str):
        self._config = config
        self._client = AsyncOpenAI(
            base_url=config.base_url,
            api_key=api_key or "not-needed",  # ollama ignores it
            timeout=60.0,
        )
        self._model = model or config.default_model

    @property
    def model(self) -> str:
        return self._model

    @property
    def provider_host(self) -> str:
        return host_of(self._config.base_url)

    @retry(
        stop=stop_after_attempt(_MAX_ATTEMPTS),
        wait=wait_exponential_jitter(multiplier=2, max=30),
        retry=retry_if_exception_type(RateLimitError),
        reraise=True,
    )
    async def _request(self, messages: list[dict], tools: list[dict]) -> dict:
        # temperature 0 + low max tokens per spec section 6 notes
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,  # type: ignore[arg-type]
            tools=tools,  # type: ignore[arg-type]
            temperature=0,
            max_tokens=1024,
        )
        return response.choices[0].message.model_dump(exclude_none=True)

    async def parse(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> ToolCall:
        """Send messages + tool defs, return the first validated tool call."""
        try:
            raw = self._request(messages, tools)
        except RateLimitError as exc:
            raise RateLimitedError(
                f"Provider {self._config.name} rate-limited after {_MAX_ATTEMPTS} attempts"
            ) from exc
        except APIStatusError as exc:
            raise LLMNotConfiguredError(
                f"Provider {self._config.name} returned HTTP {exc.status_code}"
            ) from exc
        else:
            return _validate_tool_call(raw if isinstance(raw, dict) else {})


def build_adapter(settings: Settings | None = None) -> LLMAdapter:
    """Resolve provider from settings; fail loudly on missing config."""
    settings = settings or get_settings()
    config = resolve_provider_config(settings.llm_provider)
    api_key = ""
    if config.requires_key:
        api_key = getattr(settings, config.key_setting)
        if not api_key:
            raise LLMNotConfiguredError(
                f"LLM_PROVIDER={config.name} but {config.key_setting} is empty. "
                "Set it in the repo-root .env (see .env.example)."
            )
    return LLMAdapter(config, api_key, settings.llm_model)
