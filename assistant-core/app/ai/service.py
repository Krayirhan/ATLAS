"""High-level AI service orchestration."""

from __future__ import annotations

from app.ai.context_loader import AIContextLoader
from app.ai.models import AIRequest, AIResponse
from app.ai.prompt_composer import PromptComposer
from app.ai.providers.base import AIProviderError, BaseAIProvider
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.providers.ollama_provider import OllamaAIProvider
from app.config.loader import load_assistant_settings
from app.logging.audit import write_audit
from app.paths import get_logs_dir


class AIService:
    def __init__(
        self,
        *,
        context_loader: AIContextLoader | None = None,
        prompt_composer: PromptComposer | None = None,
    ) -> None:
        self._settings = load_assistant_settings()
        self._context_loader = context_loader or AIContextLoader()
        self._prompt_composer = prompt_composer or PromptComposer()

    def ask(self, req: AIRequest) -> AIResponse:
        provider = self._provider(req.provider)
        if provider.provider_name == "ollama":
            health = provider.health_check()
            if not health.ok:
                raise AIProviderError(health.message)
            if req.warmup_only:
                return provider.warmup()
        context = self._context_loader.load(req.project)
        prompt = self._prompt_composer.compose(project=req.project, question=req.question, context=context)
        response = provider.generate(prompt=prompt, context=context)
        response.metadata["context_total_chars"] = context.metadata.get("total_chars", 0)
        response.metadata["context_limit_chars"] = context.metadata.get("max_total_chars", 0)
        self._audit(
            provider=response.provider,
            project=req.project,
            model=response.model,
            context_source_count=len(context.sources),
        )
        return response

    def provider_health(self, provider_name: str | None = None):
        return self._provider(provider_name).health_check()

    def default_provider_name(self) -> str:
        return self._settings.ai.default_provider

    def ollama_base_url(self) -> str:
        return self._settings.ai.ollama.base_url

    def warmup(self, provider_name: str | None = None) -> AIResponse:
        return self.ask(AIRequest(project="ATLAS", question="ok", provider=provider_name, warmup_only=True))

    def _provider(self, provider_name: str | None) -> BaseAIProvider:
        selected = (provider_name or self._settings.ai.default_provider).strip().lower()
        if selected == "mock":
            return MockAIProvider()
        if selected == "ollama":
            return OllamaAIProvider(self._settings.ai.ollama)
        raise AIProviderError(f"Unknown AI provider: {selected}")

    def _audit(self, *, provider: str, project: str, model: str, context_source_count: int) -> None:
        write_audit(
            event="ai_ask",
            payload={
                "provider": provider,
                "project": project,
                "model": model,
                "context_source_count": context_source_count,
            },
            logs_root=get_logs_dir(),
            stream="tool-calls",
        )
