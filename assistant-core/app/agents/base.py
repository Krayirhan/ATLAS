"""Base interface for read-only agents."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.agents.models import AgentRunRequest, AgentRunResult


class BaseAgent(ABC):
    agent_name: str
    read_only: bool = True
    can_write_files: bool = False
    can_run_commands: bool = False
    can_call_tools: bool = False

    @abstractmethod
    def run(self, request: AgentRunRequest) -> AgentRunResult:
        raise NotImplementedError
