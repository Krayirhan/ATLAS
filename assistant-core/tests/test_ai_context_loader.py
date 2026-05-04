from __future__ import annotations

from pathlib import Path

from app.ai.context_loader import AIContextLoader


def _prepare_atlas_kb(root: Path) -> Path:
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
        (kb / name).write_text(f"# {name}\ncontent\n", encoding="utf-8")
    (kb / ".env").write_text("SECRET=1\n", encoding="utf-8")
    reports = root / "workspace" / "outputs" / "reports" / "ATLAS"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "20260504T155456Z-system-health.md").write_text("# system health\nok\n", encoding="utf-8")
    return kb


def test_context_loader_lists_expected_sources(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_atlas_kb(root)
    (root / "configs" / "project-registry.json").write_text(
        (
            '{"projects":[{"name":"ATLAS","type":"python-cli","root":"'
            + str(root).replace("\\", "/")
            + '","knowledge":"'
            + str((root / "workspace" / "knowledge-base" / "ATLAS").resolve()).replace("\\", "/")
            + '","build_command":"","test_command":"python -m pytest -q","lint_command":"","command_workdir":"'
            + str((root / "assistant-core").resolve()).replace("\\", "/")
            + '","forbidden_changes":["Do not read .env files"]}]}\n'
        ),
        encoding="utf-8",
    )
    bundle = AIContextLoader().load("ATLAS")
    labels = {source.label for source in bundle.sources}
    assert "project-registry" in labels
    assert "memory-project-status" in labels
    assert "03-current-status.md" in labels
    assert "20260504T155456Z-system-health.md" in labels


def test_context_loader_does_not_read_dotenv(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_atlas_kb(root)
    (root / "configs" / "project-registry.json").write_text(
        (
            '{"projects":[{"name":"ATLAS","type":"python-cli","root":"'
            + str(root).replace("\\", "/")
            + '","knowledge":"'
            + str((root / "workspace" / "knowledge-base" / "ATLAS").resolve()).replace("\\", "/")
            + '","build_command":"","test_command":"python -m pytest -q","lint_command":"","command_workdir":"'
            + str((root / "assistant-core").resolve()).replace("\\", "/")
            + '","forbidden_changes":[]}]}\n'
        ),
        encoding="utf-8",
    )
    bundle = AIContextLoader().load("ATLAS")
    paths = {Path(source.path).name for source in bundle.sources}
    contents = "\n".join(source.content for source in bundle.sources)
    assert ".env" not in paths
    assert "SECRET=1" not in contents


def test_context_loader_applies_total_char_limit(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    kb = _prepare_atlas_kb(root)
    for name in (
        "00-project-summary.md",
        "03-current-status.md",
        "04-risk-list.md",
        "05-release-checklist.md",
        "06-next-sprints.md",
        "07-v1-rc-go-report.md",
    ):
        (kb / name).write_text(("x" * 5000) + "\n", encoding="utf-8")
    (root / "configs" / "project-registry.json").write_text(
        (
            '{"projects":[{"name":"ATLAS","type":"python-cli","root":"'
            + str(root).replace("\\", "/")
            + '","knowledge":"'
            + str((root / "workspace" / "knowledge-base" / "ATLAS").resolve()).replace("\\", "/")
            + '","build_command":"","test_command":"python -m pytest -q","lint_command":"","command_workdir":"'
            + str((root / "assistant-core").resolve()).replace("\\", "/")
            + '","forbidden_changes":[]}]}\n'
        ),
        encoding="utf-8",
    )
    bundle = AIContextLoader().load("ATLAS")
    assert bundle.metadata["total_chars"] <= bundle.metadata["max_total_chars"]
    assert all("char_count" in source.metadata for source in bundle.sources)
