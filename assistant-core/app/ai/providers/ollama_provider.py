"""Ollama provider for read-only ATLAS AI queries."""

from __future__ import annotations

import json
from urllib import error, request

from app.ai.models import AIContextBundle, AIResponse, ProviderHealth
from app.ai.providers.base import AIProviderError, BaseAIProvider
from app.config.models import OllamaSettings


class OllamaAIProvider(BaseAIProvider):
    provider_name = "ollama"

    def __init__(self, settings: OllamaSettings) -> None:
        self._settings = settings
        self.supports_streaming = bool(settings.stream)

    @property
    def model_name(self) -> str:
        return self._settings.default_model

    def generate(self, *, prompt: str, context: AIContextBundle) -> AIResponse:
        payload = {
            "model": self.model_name,
            "stream": False,
            "keep_alive": self._settings.keep_alive,
            "messages": [{"role": "user", "content": prompt}],
        }
        data = self._post_json("/api/chat", payload)
        try:
            content = str(data["message"]["content"]).strip()
        except Exception as exc:  # noqa: BLE001
            raise AIProviderError("Ollama response could not be parsed.") from exc
        return AIResponse(
            provider=self.provider_name,
            model=self.model_name,
            text=content,
            context_sources=context.sources,
            metadata={
                "done": bool(data.get("done", True)),
                "total_duration": data.get("total_duration"),
                "load_duration": data.get("load_duration"),
                "prompt_eval_duration": data.get("prompt_eval_duration"),
                "eval_duration": data.get("eval_duration"),
                "keep_alive": self._settings.keep_alive,
            },
        )

    def warmup(self) -> AIResponse:
        empty = AIContextBundle(project="ATLAS", sources=[], metadata={})
        return self.generate(prompt="ok", context=empty)

    def health_check(self) -> ProviderHealth:
        try:
            data = self._get_json("/api/tags")
        except AIProviderError as exc:
            return ProviderHealth(
                provider=self.provider_name,
                ok=False,
                model=self.model_name,
                supports_streaming=self.supports_streaming,
                message=str(exc),
            )

        models = {str(item.get("name", "")) for item in data.get("models", [])}
        if self.model_name not in models:
            return ProviderHealth(
                provider=self.provider_name,
                ok=False,
                model=self.model_name,
                supports_streaming=self.supports_streaming,
                message=f"Configured model not found: {self.model_name}. Suggested command: ollama pull {self.model_name}",
            )
        return ProviderHealth(
            provider=self.provider_name,
            ok=True,
            model=self.model_name,
            supports_streaming=self.supports_streaming,
            message="ollama reachable and model available",
        )

    def _get_json(self, path: str) -> dict:
        req = request.Request(self._url(path), method="GET")
        return self._open_json(req)

    def _post_json(self, path: str, payload: dict) -> dict:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self._url(path),
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return self._open_json(req)

    def _open_json(self, req: request.Request) -> dict:
        try:
            with request.urlopen(req, timeout=self._settings.timeout_seconds) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code == 400 and "model is required" in body.lower():
                raise AIProviderError(
                    f"Ollama rejected the request despite configured model {self.model_name}. Check Ollama server health."
                ) from exc
            if exc.code == 404 and self.model_name in body:
                raise AIProviderError(
                    f"Ollama model not found: {self.model_name}. Suggested command: ollama pull {self.model_name}"
                ) from exc
            raise AIProviderError(f"Ollama HTTP error {exc.code}: {body[:300]}") from exc
        except error.URLError as exc:
            raise AIProviderError(
                f"Ollama unreachable at {self._settings.base_url}. Ensure the Ollama service is running."
            ) from exc
        except TimeoutError as exc:
            raise AIProviderError(
                "Ollama request timed out after "
                f"{self._settings.timeout_seconds}s for model {self.model_name} at {self._settings.base_url}. "
                "Try `python -m app.cli ai warmup --provider ollama` first."
            ) from exc
        except json.JSONDecodeError as exc:
            raise AIProviderError("Ollama returned invalid JSON.") from exc

    def _url(self, path: str) -> str:
        return f"{self._settings.base_url.rstrip('/')}{path}"
