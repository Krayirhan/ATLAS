from __future__ import annotations

import os
from pathlib import Path

from typer.testing import CliRunner

from app.cli import app


def test_doctor_full_exits_zero_on_minimal_tree(isolated_atlas: Path) -> None:
    runner = CliRunner()
    r = runner.invoke(app, ["doctor", "--full"], env={**os.environ, "ATLAS_ROOT": str(isolated_atlas)})
    assert r.exit_code == 0, r.output
