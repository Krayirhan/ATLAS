from __future__ import annotations

from pathlib import Path

import pytest

from app.agents.memory_agent import MemoryAgent
from app.ai.context_loader import AIContextError


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


def test_memory_agent_builds_snapshot(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    snapshot = MemoryAgent().snapshot("ATLAS")
    labels = {source.label for source in snapshot.context_sources}
    assert snapshot.project_name == "ATLAS"
    assert "project-registry" in labels
    assert "03-current-status.md" in labels
    assert "04-risk-list.md" in labels
    assert "06-next-sprints.md" in labels
    assert snapshot.recent_reports
    assert all(source.char_count >= 0 for source in snapshot.context_sources)


def test_memory_agent_missing_optional_report_warns(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    v1_reports = root / "workspace" / "outputs" / "reports" / "V1"
    for item in v1_reports.glob("*"):
        item.unlink()
    snapshot = MemoryAgent().snapshot("ATLAS")
    assert any("audit report" in warning for warning in snapshot.warnings)


def test_memory_agent_does_not_read_dotenv_or_d_drive(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    snapshot = MemoryAgent().snapshot("ATLAS")
    joined_paths = "\n".join(source.path for source in snapshot.context_sources)
    assert ".env" not in joined_paths
    assert "D:\\ATLAS" not in joined_paths
    assert all("assistant-core\\app" not in source.path for source in snapshot.context_sources)


def test_memory_agent_unknown_project_fails(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_agent_project(root)
    with pytest.raises(AIContextError, match="Unknown project"):
        MemoryAgent().snapshot("Unknown")
