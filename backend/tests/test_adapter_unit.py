"""Adapter unit tests — validation logic only, no network calls."""

import pytest
from pydantic import ValidationError

from app.config import Settings
from app.llm import LLMNotConfiguredError
from app.llm.adapter import (
    RateLimitedError,
    ToolCall,
    ToolCallValidationError,
    _validate_tool_call,
    build_adapter,
)


def _valid_raw(openai_style: bool = True) -> dict:
    if openai_style:
        return {
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "submit_strategy_rules",
                        "arguments": '{"name": "Test", "universe": ["AAPL"]}',
                    },
                }
            ]
        }
    return {
        "tool_call_id": "call_1",
        "function": {"name": "x", "arguments": "{}"},
    }


def test_valid_tool_call_parsed():
    call = _validate_tool_call(_valid_raw())
    assert call.name == "submit_strategy_rules"
    assert call.arguments["universe"] == ["AAPL"]


def test_string_arguments_decoded():
    raw = {"tool_calls": [{"id": "c", "function": {"name": "f", "arguments": '{"a": 1}'}}]}
    assert _validate_tool_call(raw).arguments == {"a": 1}


def test_missing_name_raises():
    raw = {"tool_calls": [{"id": "c", "function": {"arguments": "{}"}}]}
    with pytest.raises(ToolCallValidationError):
        _validate_tool_call(raw)


def test_invalid_json_arguments_raises():
    raw = {"tool_calls": [{"id": "c", "function": {"name": "f", "arguments": "{not json"}}]}
    with pytest.raises(ToolCallValidationError):
        _validate_tool_call(raw)


def test_gemini_without_key_fails_loudly():
    settings = Settings(llm_provider="gemini", gemini_api_key="")
    with pytest.raises(LLMNotConfiguredError, match="gemini_api_key"):
        build_adapter(settings)


def test_ollama_without_key_works():
    settings = Settings(llm_provider="ollama", llm_model="")
    adapter = build_adapter(settings)
    assert adapter.model == "qwen2.5:7b"


def test_rate_limit_error_is_llm_error():
    assert issubclass(RateLimitedError, LLMNotConfiguredError)


def test_tool_call_rejects_empty_name():
    with pytest.raises(ValidationError):
        ToolCall(name="", arguments={})
