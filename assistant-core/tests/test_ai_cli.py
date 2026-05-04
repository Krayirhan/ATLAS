from __future__ import annotations

import os
from pathlib import Path

from typer.testing import CliRunner

from app.cli import app


def _prepare_ai_project(root: Path) -> None:
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
    (root / "workspace" / "outputs" / "reports" / "ATLAS").mkdir(parents=True, exist_ok=True)
    (root / "workspace" / "outputs" / "reports" / "ATLAS" / "20260504T155456Z-system-health.md").write_text(
        "# report\nok\n",
        encoding="utf-8",
    )
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


def test_ai_ask_provider_mock_exit_code_zero(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_ai_project(root)
    r = CliRunner().invoke(
        app,
        ["ai", "ask", "--project", "ATLAS", "--provider", "mock", "ATLAS su an ne durumda?"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 0, r.output
    assert "MOCK PROVIDER" in r.output


def test_ai_doctor_reports_mock_ok(isolated_atlas: Path, monkeypatch) -> None:
    root = isolated_atlas
    _prepare_ai_project(root)

    from app.ai.models import ProviderHealth

    monkeypatch.setattr(
        "app.commands.ai.AIService.provider_health",
        lambda self, provider_name=None: ProviderHealth(
            provider="ollama",
            ok=False,
            model="qwen2.5:7b",
            supports_streaming=False,
            message="Ollama unreachable at http://localhost:11434",
        ),
    )
    r = CliRunner().invoke(app, ["ai", "doctor"], env={**os.environ, "ATLAS_ROOT": str(root)})
    assert r.exit_code == 0, r.output
    assert "mock provider" in r.output
    assert "ok" in r.output.lower()


def test_ai_ask_show_context_lists_sources(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_ai_project(root)
    r = CliRunner().invoke(
        app,
        ["ai", "ask", "--project", "ATLAS", "--provider", "mock", "--show-context", "Sprint 29'da ne yapilmali?"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 0, r.output
    assert "Context sources" in r.output
    assert "03-current-status.md" in r.output
    assert "Total context chars:" in r.output
    assert "chars)" in r.output


def test_ai_ask_unknown_project_fails(isolated_atlas: Path) -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "ask", "--project", "Unknown", "--provider", "mock", "Durum ne?"],
        env={**os.environ, "ATLAS_ROOT": str(isolated_atlas)},
    )
    assert r.exit_code == 1
    assert "Unknown project" in r.output


def test_ai_ask_does_not_write_project_files(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    _prepare_ai_project(root)
    kb_file = root / "workspace" / "knowledge-base" / "ATLAS" / "03-current-status.md"
    before = kb_file.read_text(encoding="utf-8")
    r = CliRunner().invoke(
        app,
        ["ai", "ask", "--project", "ATLAS", "--provider", "mock", "Durum ne?"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 0, r.output
    after = kb_file.read_text(encoding="utf-8")
    assert before == after


def test_ai_warmup_command_reports_metrics(isolated_atlas: Path, monkeypatch) -> None:
    root = isolated_atlas
    _prepare_ai_project(root)

    from app.ai.models import AIResponse

    monkeypatch.setattr(
        "app.commands.ai.AIService.warmup",
        lambda self, provider_name=None: AIResponse(
            provider="ollama",
            model="qwen2.5:7b",
            text="ok",
            context_sources=[],
            metadata={"keep_alive": "30m", "total_duration": 10, "load_duration": 8},
        ),
    )
    r = CliRunner().invoke(app, ["ai", "warmup", "--provider", "ollama"], env={**os.environ, "ATLAS_ROOT": str(root)})
    assert r.exit_code == 0, r.output
    assert "model loaded / warmed" in r.output
    assert "30m" in r.output
