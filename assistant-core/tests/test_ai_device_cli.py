from __future__ import annotations

import json
import os

from typer.testing import CliRunner

from app.cli import app


def test_ai_device_rooms_exit_code_zero() -> None:
    result = CliRunner().invoke(app, ["ai", "device", "--project", "ATLAS", "--rooms"], env=os.environ)
    assert result.exit_code == 0, result.output
    assert "Salon" in result.output


def test_ai_device_list_exit_code_zero() -> None:
    result = CliRunner().invoke(app, ["ai", "device", "--project", "ATLAS", "--list"], env=os.environ)
    assert result.exit_code == 0, result.output
    assert "Salon Isigi" in result.output


def test_ai_device_plan_salon_light() -> None:
    result = CliRunner().invoke(app, ["ai", "device", "--project", "ATLAS", "Salon isigini ac"], env=os.environ)
    assert result.exit_code == 0, result.output
    assert "planned" in result.output.lower()


def test_ai_device_show_plan_ambiguous() -> None:
    result = CliRunner().invoke(app, ["ai", "device", "--project", "ATLAS", "--show-plan", "Isigi ac"], env=os.environ)
    assert result.exit_code == 0, result.output
    assert "Clarification" in result.output


def test_ai_device_json_temperature() -> None:
    result = CliRunner().invoke(app, ["ai", "device", "--project", "ATLAS", "--json", "Klimayi 24 derece yap"], env=os.environ)
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "planned"
    assert payload["plan"]["requires_confirmation"] is True
