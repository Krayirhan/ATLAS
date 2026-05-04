from __future__ import annotations

import os
from pathlib import Path

from typer.testing import CliRunner

from app.cli import app


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


def test_ai_memory_cli_exit_zero(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    r = CliRunner().invoke(app, ["ai", "memory", "--project", "ATLAS"], env={**os.environ, "ATLAS_ROOT": str(root)})
    assert r.exit_code == 0, r.output
    assert "Project" in r.output


def test_ai_ask_agent_mock_exit_zero(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    r = CliRunner().invoke(
        app,
        ["ai", "ask-agent", "--project", "ATLAS", "--provider", "mock", "ATLAS su an ne durumda?"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 0, r.output
    assert "MOCK PROVIDER" in r.output


def test_ai_ask_agent_show_sources_and_context(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    r = CliRunner().invoke(
        app,
        ["ai", "ask-agent", "--project", "ATLAS", "--provider", "mock", "--show-sources", "--show-context", "Riskler ne?"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 0, r.output
    assert "Sources" in r.output
    assert "Total context chars:" in r.output
    assert "Prompt body hidden by design." in r.output


def test_existing_ai_ask_still_works(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    r = CliRunner().invoke(
        app,
        ["ai", "ask", "--project", "ATLAS", "--provider", "mock", "Durum ne?"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 0, r.output
