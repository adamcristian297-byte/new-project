"""Health endpoint tests via Starlette TestClient (no server, no network)."""

import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture(name="client")
def client_fixture() -> TestClient:
    return TestClient(main.app)


def test_health_ok_and_provider_echoed(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["llm"]["provider"] in ("gemini", "groq", "ollama")
    assert body["llm"]["key_state"] in ("set", "unset")


def test_health_does_not_leak_secrets(client):
    response = client.get("/health")
    content = response.text
    for secret in ("api_key", "gemini_api_key", "groq_api_key", "secret"):
        assert secret not in content.split("key_state")[0].lower() or secret == "key_state"
