from __future__ import annotations

import io
import json
from urllib import error

import pytest

from app.ai.models import AIContextBundle
from app.ai.providers.base import AIProviderError
from app.ai.providers.ollama_provider import OllamaAIProvider
from app.config.models import OllamaSettings


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_ollama_provider_generate_uses_http(monkeypatch) -> None:
    provider = OllamaAIProvider(OllamaSettings())

    def _fake_urlopen(req, timeout):
        assert req.full_url == "http://localhost:11434/api/chat"
        assert timeout == 300
        body = json.loads(req.data.decode("utf-8"))
        assert body["model"] == "qwen2.5:7b"
        assert body["stream"] is False
        assert body["keep_alive"] == "30m"
        return _FakeResponse(
            {
                "message": {"content": "ATLAS iyi durumda"},
                "done": True,
                "total_duration": 10,
                "load_duration": 4,
                "prompt_eval_duration": 3,
                "eval_duration": 1,
            }
        )

    monkeypatch.setattr("app.ai.providers.ollama_provider.request.urlopen", _fake_urlopen)
    response = provider.generate(prompt="prompt", context=AIContextBundle(project="ATLAS", sources=[]))
    assert response.text == "ATLAS iyi durumda"
    assert response.metadata["keep_alive"] == "30m"
    assert response.metadata["total_duration"] == 10


def test_ollama_provider_unavailable_is_graceful(monkeypatch) -> None:
    provider = OllamaAIProvider(OllamaSettings())

    def _fake_urlopen(req, timeout):
        raise error.URLError("connection refused")

    monkeypatch.setattr("app.ai.providers.ollama_provider.request.urlopen", _fake_urlopen)
    with pytest.raises(AIProviderError, match="Ollama unreachable"):
        provider.health_check()
        provider.generate(prompt="prompt", context=AIContextBundle(project="ATLAS", sources=[]))


def test_ollama_provider_missing_model_is_graceful(monkeypatch) -> None:
    provider = OllamaAIProvider(OllamaSettings())

    def _fake_urlopen(req, timeout):
        payload = b'{"error":"model \\"qwen2.5:7b\\" not found"}'
        raise error.HTTPError(req.full_url, 404, "not found", hdrs=None, fp=io.BytesIO(payload))

    monkeypatch.setattr("app.ai.providers.ollama_provider.request.urlopen", _fake_urlopen)
    with pytest.raises(AIProviderError, match="ollama pull qwen2.5:7b"):
        provider.generate(prompt="prompt", context=AIContextBundle(project="ATLAS", sources=[]))


def test_ollama_provider_timeout_message_includes_debug_fields(monkeypatch) -> None:
    provider = OllamaAIProvider(OllamaSettings())

    def _fake_urlopen(req, timeout):
        raise TimeoutError("slow")

    monkeypatch.setattr("app.ai.providers.ollama_provider.request.urlopen", _fake_urlopen)
    with pytest.raises(AIProviderError, match="300s"):
        provider.generate(prompt="prompt", context=AIContextBundle(project="ATLAS", sources=[]))
