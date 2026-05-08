from __future__ import annotations

import json
import os

from typer.testing import CliRunner

from app.cli import app


def test_ai_home_preview_light_exit_code_zero() -> None:
    result = CliRunner().invoke(app, ["ai", "home-preview", "--project", "ATLAS", "Salon isigini ac"], env=os.environ)
    assert result.exit_code == 0, result.output
    assert "awaiting_confirmation" in result.output.lower()


def test_ai_home_preview_show_plan() -> None:
    result = CliRunner().invoke(app, ["ai", "home-preview", "--project", "ATLAS", "--show-plan", "Klimayi 24 derece yap"], env=os.environ)
    assert result.exit_code == 0, result.output
    assert "Plan" in result.output
    assert "State Write" in result.output


def test_ai_home_preview_json_ambiguous() -> None:
    result = CliRunner().invoke(app, ["ai", "home-preview", "--project", "ATLAS", "--json", "Isigi ac"], env=os.environ)
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["result"]["status"] == "unsupported"


def test_ai_home_preview_adapter_status() -> None:
    result = CliRunner().invoke(app, ["ai", "home-preview", "--project", "ATLAS", "--adapter-status"], env=os.environ)
    assert result.exit_code == 0, result.output
    assert "execution_supported" in result.output


def test_ai_home_preview_capabilities() -> None:
    result = CliRunner().invoke(app, ["ai", "home-preview", "--project", "ATLAS", "--capabilities"], env=os.environ)
    assert result.exit_code == 0, result.output
    assert "state_query" in result.output
