from __future__ import annotations

from pathlib import Path

import pytest

from app.agents.memory_agent import MemoryAgent
from app.agents.models import ProjectQARequest
from app.agents.project_qa_agent import ProjectQAAgent
from app.ai.providers.base import AIProviderError


def _prepare_agent_project(root: Path) -> None:
    kb = root / "workspace" / "knowledge-base" / "ATLAS"
    kb.mkdir(parents=True, exist_ok=True)
    for name in (
        "00-project-summary.md",
        "03-current-status.md",
        "04-risk-list.md",
        "05-release-checklist.md",
        "06-next-sprints.md",
        "07-v1-rc-go-report.md",
    ):
        (kb / name).write_text(f"# {name}\nicerik\n", encoding="utf-8")
    atlas_reports = root / "workspace" / "outputs" / "reports" / "ATLAS"
    atlas_reports.mkdir(parents=True, exist_ok=True)
    (atlas_reports / "20260504T155456Z-system-health.md").write_text("# health\nok\n", encoding="utf-8")
    v1_reports = root / "workspace" / "outputs" / "reports" / "V1"
    v1_reports.mkdir(parents=True, exist_ok=True)
    (v1_reports / "v1-rc-audit-20260504T111111Z.md").write_text("# audit\ngo\n", encoding="utf-8")
    (root / "configs" / "project-registry.json").write_text(
        (
            '{"projects":[{"name":"ATLAS","type":"python-cli","root":"'
            + str(root).replace("\\", "/")
            + '","knowledge":"'
            + str(kb.resolve()).replace("\\", "/")
            + '","build_command":"","test_command":"python -m pytest -q","lint_command":"","command_workdir":"'
            + str((root / "assistant-core").resolve()).replace("\\", "/")
            + '","forbidden_changes":[]}]}\n'
        ),
        encoding="utf-8",
    )


def test_project_qa_agent_mock_provider_works(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    agent = ProjectQAAgent(memory_agent=MemoryAgent())
    result = agent.answer(ProjectQARequest(project_name="ATLAS", question="Durum ne?", provider="mock"))
    assert result.status == "ok"
    assert "Read-only advisory mode." in result.answer
    assert "MOCK PROVIDER" in result.answer
    assert result.sources


def test_project_qa_agent_unknown_project_fails(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    agent = ProjectQAAgent(memory_agent=MemoryAgent())
    with pytest.raises(Exception, match="Unknown project"):
        agent.answer(ProjectQARequest(project_name="Unknown", question="Durum ne?", provider="mock"))


def test_project_qa_agent_ollama_timeout_is_graceful(isolated_atlas_with_memory: Path, monkeypatch) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    agent = ProjectQAAgent(memory_agent=MemoryAgent())

    class _FakeProvider:
        provider_name = "ollama"

        def health_check(self):
            from app.ai.models import ProviderHealth

            return ProviderHealth("ollama", True, "qwen2.5:7b", False, "ollama reachable and model available")

        def generate(self, *, prompt: str, context):
            raise AIProviderError("timeout")

    monkeypatch.setattr(agent, "_provider", lambda provider_name: _FakeProvider())
    result = agent.answer(ProjectQARequest(project_name="ATLAS", question="Durum ne?", provider="ollama"))
    assert result.status == "warning"
    assert "Read-only" in result.answer
    assert "timeout" in "\n".join(result.warnings)


def test_project_qa_agent_ollama_provider_mocked_success(isolated_atlas_with_memory: Path, monkeypatch) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    agent = ProjectQAAgent(memory_agent=MemoryAgent())

    class _FakeProvider:
        provider_name = "ollama"

        def health_check(self):
            from app.ai.models import ProviderHealth

            return ProviderHealth("ollama", True, "qwen2.5:7b", False, "ollama reachable and model available")

        def generate(self, *, prompt: str, context):
            from app.ai.models import AIResponse

            return AIResponse("ollama", "qwen2.5:7b", "ATLAS GO durumda.", [], {"done": True})

    monkeypatch.setattr(agent, "_provider", lambda provider_name: _FakeProvider())
    result = agent.answer(ProjectQARequest(project_name="ATLAS", question="Durum ne?", provider="ollama"))
    assert result.status == "ok"
    assert "ATLAS GO durumda." in result.answer
