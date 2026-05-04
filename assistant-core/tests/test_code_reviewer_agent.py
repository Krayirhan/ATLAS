from __future__ import annotations

from pathlib import Path

import pytest

from app.agents.code_reviewer_agent import CodeReviewerAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.models import CodeReviewRequest
from app.ai.providers.base import AIProviderError


def _prepare_agent_project(root: Path) -> None:
    kb = root / "workspace" / "knowledge-base" / "ATLAS"
    kb.mkdir(parents=True, exist_ok=True)
    assistant = root / "assistant-core"
    (assistant / "app" / "ai").mkdir(parents=True, exist_ok=True)
    (assistant / "app" / "agents").mkdir(parents=True, exist_ok=True)
    (assistant / "app" / "commands").mkdir(parents=True, exist_ok=True)
    (assistant / "app" / "safety").mkdir(parents=True, exist_ok=True)
    (assistant / "app" / "config").mkdir(parents=True, exist_ok=True)
    (assistant / "app" / "mcp").mkdir(parents=True, exist_ok=True)
    (assistant / "tests").mkdir(parents=True, exist_ok=True)
    (assistant / "README.md").write_text("# assistant-core\n", encoding="utf-8")
    (assistant / "app" / "commands" / "ai.py").write_text("def ai_review():\n    return 'ok'\n", encoding="utf-8")
    (assistant / "app" / "commands" / "command.py").write_text("def command_check():\n    return 'ok'\n", encoding="utf-8")
    (assistant / "app" / "safety" / "policy.py").write_text("READ_ONLY = True\n", encoding="utf-8")
    (assistant / "app" / "ai" / "service.py").write_text("class AIService:\n    pass\n", encoding="utf-8")
    (assistant / "app" / "agents" / "memory_agent.py").write_text("class MemoryAgent:\n    pass\n", encoding="utf-8")
    (assistant / "app" / "config" / "loader.py").write_text("def load():\n    return {}\n", encoding="utf-8")
    (assistant / "app" / "mcp" / "generator.py").write_text("def generate():\n    return {}\n", encoding="utf-8")
    (assistant / "tests" / "test_ai_cli.py").write_text("def test_ai():\n    assert True\n", encoding="utf-8")
    (assistant / "tests" / "test_memory_agent.py").write_text("def test_agent():\n    assert True\n", encoding="utf-8")
    for name in (
        "00-project-summary.md",
        "03-current-status.md",
        "04-risk-list.md",
        "05-release-checklist.md",
        "06-next-sprints.md",
        "07-v1-rc-go-report.md",
        "08-ai-layer-design.md",
        "11-ai-context-contract.md",
        "13-sprint-28-ai-layer-foundation-plan.md",
        "14-sprint-29-memory-agent-projectqa-plan.md",
        "15-ai-security-boundaries.md",
    ):
        (kb / name).write_text(f"# {name}\nicerik\n", encoding="utf-8")
    (kb / ".env").write_text("SECRET=1\n", encoding="utf-8")
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
            + '","forbidden_changes":["Do not read .env files","Do not use D:/ATLAS"]}]}\n'
        ),
        encoding="utf-8",
    )


def test_code_reviewer_agent_read_only_flags() -> None:
    agent = CodeReviewerAgent()
    assert agent.read_only is True
    assert agent.can_write_files is False
    assert agent.can_run_commands is False
    assert agent.can_call_tools is False


def test_code_reviewer_agent_safety_scope_bounded(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    result = CodeReviewerAgent(memory_agent=MemoryAgent()).review(
        CodeReviewRequest(project_name="ATLAS", provider="mock", scope="safety")
    )
    assert result.status == "ok"
    assert result.findings
    assert result.sources
    assert all(".env" not in source.path for source in result.sources)
    assert all("D:\\ATLAS" not in source.path for source in result.sources)


def test_code_reviewer_agent_ai_layer_scope_includes_agent_or_ai_files(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    result = CodeReviewerAgent(memory_agent=MemoryAgent()).review(
        CodeReviewRequest(project_name="ATLAS", provider="mock", scope="ai-layer")
    )
    assert result.sources
    normalized_paths = [source.path.replace("/", "\\").lower() for source in result.sources]
    assert any("\\app\\ai\\" in path or "\\app\\agents\\" in path for path in normalized_paths)


def test_code_reviewer_agent_unknown_scope_graceful(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    with pytest.raises(Exception, match="Unknown review scope"):
        CodeReviewerAgent(memory_agent=MemoryAgent()).review(
            CodeReviewRequest(project_name="ATLAS", provider="mock", scope="unknown")  # type: ignore[arg-type]
        )


def test_code_reviewer_agent_max_files_and_chars(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    result = CodeReviewerAgent(memory_agent=MemoryAgent()).review(
        CodeReviewRequest(project_name="ATLAS", provider="mock", scope="docs", max_files=2, max_chars_per_file=20)
    )
    assert len(result.sources) <= 2
    assert all(source.char_count <= 20 for source in result.sources)


def test_code_reviewer_agent_mock_returns_structured_review(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    result = CodeReviewerAgent(memory_agent=MemoryAgent()).review(
        CodeReviewRequest(project_name="ATLAS", provider="mock", scope="config")
    )
    assert "Read-only review mode." in result.summary
    assert result.recommendations
    assert result.test_suggestions


def test_code_reviewer_agent_ollama_timeout_graceful(isolated_atlas_with_memory: Path, monkeypatch) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    agent = CodeReviewerAgent(memory_agent=MemoryAgent())

    def _raise_timeout(*_args, **_kwargs):
        raise AIProviderError("timeout")

    monkeypatch.setattr(agent, "_ollama_review_summary", _raise_timeout)
    result = agent.review(CodeReviewRequest(project_name="ATLAS", provider="ollama", scope="config"))
    assert result.status == "warning"
    assert "timeout" in "\n".join(result.warnings)


def test_code_reviewer_agent_ollama_mocked_success(isolated_atlas_with_memory: Path, monkeypatch) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    agent = CodeReviewerAgent(memory_agent=MemoryAgent())
    monkeypatch.setattr(agent, "_ollama_review_summary", lambda *args, **kwargs: "Review hazir. Onay gerekli.")
    result = agent.review(CodeReviewRequest(project_name="ATLAS", provider="ollama", scope="config"))
    assert result.status == "ok"
    assert "Onay gerekli" in result.summary


def test_code_reviewer_agent_source_metadata_present(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    result = CodeReviewerAgent(memory_agent=MemoryAgent()).review(
        CodeReviewRequest(project_name="ATLAS", provider="mock", scope="all-light")
    )
    assert result.sources
    assert all(source.char_count >= 0 for source in result.sources)
    assert all(source.metadata.get("scope") == "all-light" for source in result.sources)
