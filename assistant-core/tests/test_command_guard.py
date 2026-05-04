from __future__ import annotations

import os
from pathlib import Path

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


def test_command_check_allows_pytest(isolated_atlas: Path) -> None:
    root = isolated_atlas
    runner = CliRunner()
    r = runner.invoke(
        app,
        ["command", "check", "Demo", "--cmd", "python -m pytest -q"],
        env={**os.environ, "ATLAS_ROOT": str(root)},
    )
    assert r.exit_code == 0
