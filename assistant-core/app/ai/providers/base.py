"""Base interfaces for AI providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.models import AIContextBundle, AIResponse, ProviderHealth


class AIProviderError(RuntimeError):
    """Provider-specific runtime error."""


class BaseAIProvider(ABC):
    provider_name: str
    supports_streaming: bool = False

    @abstractmethod
    def generate(self, *, prompt: str, context: AIContextBundle) -> AIResponse:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> ProviderHealth:
        raise NotImplementedError
