from __future__ import annotations

import json
import os
from pathlib import Path

from typer.testing import CliRunner

from app.cli import app


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


def test_ai_review_mock_exit_zero(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    r = CliRunner().invoke(
        app,
        ["ai", "review", "--project", "ATLAS", "--provider", "mock", "--scope", "safety"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 0, r.output
    assert "Read-only review mode." in r.output


def test_ai_review_show_sources(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    r = CliRunner().invoke(
        app,
        ["ai", "review", "--project", "ATLAS", "--provider", "mock", "--scope", "ai-layer", "--show-sources"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 0, r.output
    assert "Sources" in r.output


def test_ai_review_json_output(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    r = CliRunner().invoke(
        app,
        ["ai", "review", "--project", "ATLAS", "--provider", "mock", "--scope", "config", "--json"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 0, r.output
    data = json.loads(r.output)
    assert data["project_name"] == "ATLAS"
    assert data["findings"]


def test_ai_review_unknown_scope_fails_cleanly(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    r = CliRunner().invoke(
        app,
        ["ai", "review", "--project", "ATLAS", "--provider", "mock", "--scope", "unknown"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 1
    assert "Unknown review scope" in r.output


def test_existing_ai_plan_and_ask_agent_still_work(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    runner = CliRunner()
    r1 = runner.invoke(
        app,
        ["ai", "plan", "--project", "ATLAS", "--provider", "mock", "--goal", "Sprint 32 planla"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    r2 = runner.invoke(
        app,
        ["ai", "ask-agent", "--project", "ATLAS", "--provider", "mock", "Durum ne?"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r1.exit_code == 0, r1.output
    assert r2.exit_code == 0, r2.output
