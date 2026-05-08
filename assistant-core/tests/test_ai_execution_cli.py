from __future__ import annotations

import json

from typer.testing import CliRunner

from app.cli import app


runner = CliRunner()


def test_ai_execution_preview_exit_zero() -> None:
    result = runner.invoke(app, ["ai", "execution", "--project", "ATLAS", "--preview", "Chrome'u ac"])
    assert result.exit_code == 0, result.output
    assert "gercek islem yapilmadi" in result.output.lower()


def test_ai_execution_blocked_secret_read() -> None:
    result = runner.invoke(app, ["ai", "execution", "--project", "ATLAS", "--preview", "Sifrelerimi oku"])
    assert result.exit_code == 0, result.output
    assert "blocked" in result.output.lower()


def test_ai_execution_home_action_not_eligible() -> None:
    result = runner.invoke(app, ["ai", "execution", "--project", "ATLAS", "--preview", "Salon isigini ac"])
    assert result.exit_code == 0, result.output
    assert "eligible" in result.output.lower()
    assert "false" in result.output.lower()


def test_ai_execution_check_allowlist() -> None:
    result = runner.invoke(app, ["ai", "execution", "--project", "ATLAS", "--check-allowlist", "pc.open_app"])
    assert result.exit_code == 0, result.output
    assert "Allowed" in result.output
    assert "True" in result.output


def test_ai_execution_json_is_valid() -> None:
    result = runner.invoke(app, ["ai", "execution", "--project", "ATLAS", "--json", "--preview", "Chrome'u ac"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["plan"]["eligible"] is True


def test_ai_execution_execute_does_not_run_real_execution() -> None:
    result = runner.invoke(app, ["ai", "execution", "--project", "ATLAS", "--execute", "--preview", "Chrome'u ac"])
    assert result.exit_code == 0, result.output
    assert "gercek islem yapilmadi" in result.output.lower()
