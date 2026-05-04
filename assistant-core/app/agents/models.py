"""Models for the read-only agent layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentContextSource:
    source_type: str
    label: str
    path: str
    char_count: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentRunRequest:
    project_name: str
    question: str = ""
    provider: str | None = None
    show_sources: bool = False
    show_context: bool = False


@dataclass(slots=True)
class AgentRunResult:
    agent_name: str
    project_name: str
    status: str
    answer: str
    sources: list[AgentContextSource]
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MemorySnapshot:
    project_name: str
    project_type: str
    root: str
    knowledge_path: str
    current_status: str
    risks: str
    next_sprints: str
    release_status: str
    recent_reports: list[str]
    decisions: list[tuple[str, str]]
    context_sources: list[AgentContextSource]
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ProjectQARequest:
    project_name: str
    question: str
    provider: str | None = None
    show_sources: bool = False
    show_context: bool = False


@dataclass(slots=True)
class ProjectQAResult:
    agent_name: str
    project_name: str
    status: str
    answer: str
    sources: list[AgentContextSource]
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
