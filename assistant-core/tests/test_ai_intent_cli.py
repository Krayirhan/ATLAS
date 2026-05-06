from __future__ import annotations

import json
import os

from typer.testing import CliRunner

from app.cli import app


def test_ai_intent_exit_code_zero() -> None:
    result = CliRunner().invoke(
        app,
        ["ai", "intent", "--project", "ATLAS", "Chrome'u ac"],
        env=os.environ,
    )
    assert result.exit_code == 0, result.output
    assert "pc.open_app" in result.output


def test_ai_intent_show_preview_displays_permission() -> None:
    result = CliRunner().invoke(
        app,
        ["ai", "intent", "--project", "ATLAS", "--show-preview", "Salon isigini ac"],
        env=os.environ,
    )
    assert result.exit_code == 0, result.output
    assert "confirmation_required" in result.output


def test_ai_intent_json_outputs_valid_json() -> None:
    result = CliRunner().invoke(
        app,
        ["ai", "intent", "--project", "ATLAS", "--json", "Sifrelerimi oku"],
        env=os.environ,
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["intent"]["category"] == "blocked"
    assert payload["permission_decision"]["status"] == "blocked"


def test_ai_intent_clarification_output() -> None:
    result = CliRunner().invoke(
        app,
        ["ai", "intent", "--project", "ATLAS", "--show-preview", "Isigi ac"],
        env=os.environ,
    )
    assert result.exit_code == 0, result.output
    assert "clarification_required" in result.output


def test_ai_intent_blocked_output() -> None:
    result = CliRunner().invoke(
        app,
        ["ai", "intent", "--project", "ATLAS", "--show-preview", "Sifrelerimi oku"],
        env=os.environ,
    )
    assert result.exit_code == 0, result.output
    assert "blocked" in result.output.lower()


def test_ai_intent_voice_source_supported() -> None:
    result = CliRunner().invoke(
        app,
        ["ai", "intent", "--project", "ATLAS", "--source", "voice", "--show-preview", "Bilgisayari kapat"],
        env=os.environ,
    )
    assert result.exit_code == 0, result.output
    assert "Sesli komut" in result.output
