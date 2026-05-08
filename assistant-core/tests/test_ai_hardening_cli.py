from __future__ import annotations

import json

from typer.testing import CliRunner

from app.cli import app


runner = CliRunner()


def test_ai_hardening_safety_exit_code_zero() -> None:
    result = runner.invoke(app, ["ai", "hardening", "--project", "ATLAS", "--safety"])
    assert result.exit_code == 0, result.output
    assert "Safety" in result.output


def test_ai_hardening_latency_exit_code_zero() -> None:
    result = runner.invoke(app, ["ai", "hardening", "--project", "ATLAS", "--latency"])
    assert result.exit_code == 0, result.output
    assert "Latency" in result.output


def test_ai_hardening_all_json_outputs_valid_json() -> None:
    result = runner.invoke(app, ["ai", "hardening", "--project", "ATLAS", "--all", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["project_name"] == "ATLAS"
    assert payload["safety_report"]["failed"] == 0
    assert payload["latency_report"]["total_measurements"] == 8
    first_flags = payload["safety_report"]["checks"][0]["flags"]
    assert first_flags["real_execution_attempted"] is False
    assert first_flags["allowlist_required"] is True


def test_ai_hardening_markdown_no_write_works() -> None:
    result = runner.invoke(app, ["ai", "hardening", "--project", "ATLAS", "--all", "--markdown", "--no-write"])
    assert result.exit_code == 0, result.output
    assert "ATLAS Sprint 51" in result.output


def test_ai_hardening_output_path_outside_workspace_blocked() -> None:
    result = runner.invoke(
        app,
        [
            "ai",
            "hardening",
            "--project",
            "ATLAS",
            "--all",
            "--markdown",
            "--output",
            "..\\outside-hardening.md",
        ],
    )
    assert result.exit_code == 1
    assert "workspace/outputs/hardening" in result.output
