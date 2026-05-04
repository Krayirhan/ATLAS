from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from app.cli import app


def test_command_check_blocks_git_reset(isolated_atlas: Path) -> None:
    root = isolated_atlas
    runner = CliRunner()
    r = runner.invoke(
        app,
        ["command", "check", "Demo", "--cmd", "git reset --hard"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 2


def test_command_check_blocks_git_clean(isolated_atlas: Path) -> None:
    root = isolated_atlas
    r = CliRunner().invoke(
        app,
        ["command", "check", "Demo", "--cmd", "git clean -fd"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 2


def test_command_check_blocks_git_push_force(isolated_atlas: Path) -> None:
    root = isolated_atlas
    r = CliRunner().invoke(
        app,
        ["command", "check", "Demo", "--cmd", "git push --force"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 2


def test_command_check_blocks_remove_item_recurse(isolated_atlas: Path) -> None:
    root = isolated_atlas
    r = CliRunner().invoke(
        app,
        ["command", "check", "Demo", "--cmd", "Remove-Item -Recurse"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 2


def test_command_check_blocks_invoke_expression(isolated_atlas: Path) -> None:
    root = isolated_atlas
    r = CliRunner().invoke(
        app,
        ["command", "check", "Demo", "--cmd", "Invoke-Expression"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 2


def test_command_check_allows_pytest(isolated_atlas: Path) -> None:
    root = isolated_atlas
    runner = CliRunner()
    r = runner.invoke(
        app,
        ["command", "check", "Demo", "--cmd", "python -m pytest -q"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 0


def test_command_preview_test_type_no_execution(isolated_atlas: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = isolated_atlas
    monkeypatch.setenv("ATLAS_ROOT", str(root))
    data = json.loads((root / "configs" / "project-registry.json").read_text(encoding="utf-8"))
    data["projects"][0]["test_command"] = "python -m pytest -q"
    data["projects"][0]["command_workdir"] = str(root / "assistant-core")
    (root / "configs" / "project-registry.json").write_text(json.dumps(data) + "\n", encoding="utf-8")
    from typer.testing import CliRunner

    runner = CliRunner()
    r = runner.invoke(app, ["command", "preview", "Demo", "--type", "test"])
    assert r.exit_code == 0
    assert "Preview only" in r.output or "preview" in r.output.lower()
    assert "pytest" in r.output
