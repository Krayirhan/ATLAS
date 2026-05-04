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


def test_logs_project_last_limits_output(isolated_atlas: Path) -> None:
    root = isolated_atlas
    logf = root / "logs" / "tool-calls" / "2021-01-01.jsonl"
    lines_out = []
    for i in range(5):
        lines_out.append(json.dumps({"ts": f"2021-01-01T00:00:0{i}Z", "payload": {"project": "ATLAS"}}))
    logf.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    r = CliRunner().invoke(app, ["logs", "project", "ATLAS", "--last", "2"], env={"ATLAS_ROOT": str(root)})
    assert r.exit_code == 0
    assert r.output.count("ATLAS") >= 2


def test_logs_project_scrubs_sensitive_keys(isolated_atlas: Path) -> None:
    root = isolated_atlas
    logf = root / "logs" / "sessions" / "2022-01-01.jsonl"
    rec = {"ts": "2022-01-01T00:00:00Z", "project": "ATLAS", "payload": {"api_key": "secret123"}}
    logf.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    r = CliRunner().invoke(app, ["logs", "project", "ATLAS", "--last", "3"], env={"ATLAS_ROOT": str(root)})
    assert r.exit_code == 0
    assert "secret123" not in r.output
    assert "[redacted]" in r.output
