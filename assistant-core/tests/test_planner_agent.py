from __future__ import annotations

from pathlib import Path

from app.agents.memory_agent import MemoryAgent
from app.agents.models import PlannerRequest
from app.agents.planner_agent import PlannerAgent
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
        "13-sprint-28-ai-layer-foundation-plan.md",
        "14-sprint-29-memory-agent-projectqa-plan.md",
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


def test_planner_agent_read_only_flags() -> None:
    agent = PlannerAgent()
    assert agent.read_only is True
    assert agent.can_write_files is False
    assert agent.can_run_commands is False
    assert agent.can_call_tools is False


def test_planner_agent_mock_plan(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    agent = PlannerAgent(memory_agent=MemoryAgent())
    result = agent.plan(PlannerRequest(project_name="ATLAS", goal="Sprint 31 için CodeReviewerAgent hazırlığı yap", provider="mock"))
    assert result.status == "ok"
    assert "Objective:" in result.plan_summary
    assert "Scope:" in result.plan_summary
    assert "Out of scope:" in result.plan_summary
    assert "Risks:" in result.plan_summary
    assert "Acceptance criteria:" in result.plan_summary
    assert "Test plan:" in result.plan_summary
    assert result.sources


def test_planner_agent_unknown_project_graceful(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    agent = PlannerAgent(memory_agent=MemoryAgent())
    try:
        agent.plan(PlannerRequest(project_name="Unknown", goal="x", provider="mock"))
    except Exception as exc:  # noqa: BLE001
        assert "Unknown project" in str(exc)


def test_planner_agent_ollama_timeout_graceful(isolated_atlas_with_memory: Path, monkeypatch) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    agent = PlannerAgent(memory_agent=MemoryAgent())

    def _fake_ollama(goal, snapshot, sources):
        raise AIProviderError("timeout")

    monkeypatch.setattr(agent, "_ollama_plan_summary", _fake_ollama)
    result = agent.plan(PlannerRequest(project_name="ATLAS", goal="x", provider="ollama"))
    assert result.status == "warning"
    assert "timeout" in "\n".join(result.warnings)


def test_planner_agent_ollama_mocked_success(isolated_atlas_with_memory: Path, monkeypatch) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    agent = PlannerAgent(memory_agent=MemoryAgent())

    monkeypatch.setattr(agent, "_ollama_plan_summary", lambda goal, snapshot, sources: "Plan hazir. Onay gerekli.")
    result = agent.plan(PlannerRequest(project_name="ATLAS", goal="x", provider="ollama"))
    assert result.status == "ok"
    assert "Onay gerekli" in result.plan_summary
