"""Mock AI provider for tests and safe fallback."""

from __future__ import annotations

from app.ai.models import AIContextBundle, AIResponse, ProviderHealth
from app.ai.providers.base import BaseAIProvider


class MockAIProvider(BaseAIProvider):
    provider_name = "mock"
    supports_streaming = False

    def generate(self, *, prompt: str, context: AIContextBundle) -> AIResponse:
        labels = ", ".join(source.label for source in context.sources[:6]) or "(no sources)"
        text = (
            "[MOCK PROVIDER] Bu yanit gercek bir LLM cagrisindan gelmiyor.\n\n"
            f"Proje: {context.project}\n"
            f"Soru ozeti: {prompt.splitlines()[-1][:200]}\n"
            f"Context kaynaklari ({len(context.sources)}): {labels}"
        )
        return AIResponse(
            provider=self.provider_name,
            model="mock-readonly",
            text=text,
            context_sources=context.sources,
            metadata={"mock": True},
        )

    def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            provider=self.provider_name,
            ok=True,
            model="mock-readonly",
            supports_streaming=self.supports_streaming,
            message="mock provider ready",
        )
