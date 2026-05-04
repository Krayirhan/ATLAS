from __future__ import annotations

import os
from pathlib import Path

from typer.testing import CliRunner

from app.cli import app

from support_registry import write_atlas_only_registry


def test_system_health_report_contains_core_sections(isolated_atlas_with_memory: Path) -> None:
    root = isolated_atlas_with_memory
    write_atlas_only_registry(root)
    runner = CliRunner()
    env = {**os.environ, "ATLAS_ROOT": str(root), "ATLAS_REPORT_LIGHT": "1"}
    r0 = runner.invoke(app, ["memory", "sync-projects"], env=env)
    assert r0.exit_code == 0, r0.output
    r = runner.invoke(
        app,
        ["report", "create", "ATLAS", "--type", "system-health"],
        env=env,
    )
    assert r.exit_code == 0, r.output
    out_dir = root / "workspace" / "outputs" / "reports" / "ATLAS"
    paths = sorted(out_dir.glob("*system-health*.md"))
    assert paths, "expected report markdown under workspace/outputs/reports/ATLAS"
    path = paths[-1]
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    for heading in (
        "## Report type",
        "## Project name",
        "## Root path",
        "## Safety status",
        "## MCP status",
        "## Doctor status",
        "## Test status",
        "## GO / CONDITIONAL / NO-GO",
    ):
        assert heading in text
