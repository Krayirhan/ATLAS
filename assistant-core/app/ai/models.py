"""Models for the read-only AI layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AIContextSource:
    kind: str
    label: str
    path: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AIContextBundle:
    project: str
    sources: list[AIContextSource]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AIRequest:
    project: str
    question: str
    provider: str | None = None
    show_context: bool = False
    warmup_only: bool = False


@dataclass(slots=True)
class AIResponse:
    provider: str
    model: str
    text: str
    context_sources: list[AIContextSource]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderHealth:
    provider: str
    ok: bool
    model: str
    supports_streaming: bool
    message: str
