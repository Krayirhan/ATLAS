from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from app.cli import app


def test_logs_project_filters_and_skips_bad_json(isolated_atlas: Path) -> None:
    root = isolated_atlas
    logf = root / "logs" / "tool-calls" / "2020-01-01.jsonl"
    rec_ok = {"ts": "2020-01-01T00:00:00Z", "event": "x", "payload": {"project": "ATLAS"}}
    logf.write_text(
        json.dumps(rec_ok)
        + "\nnot-json\n"
        + json.dumps({"ts": "2020-01-01T00:01:00Z", "event": "y", "payload": {"project": "Other"}})
        + "\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    r = runner.invoke(app, ["logs", "project", "ATLAS", "--last", "5"], env={"ATLAS_ROOT": str(root)})
    assert r.exit_code == 0
    assert "ATLAS" in r.output
    assert "Other" not in r.output
    assert "Skipping invalid JSONL" in r.output or "skip" in r.output.lower()
