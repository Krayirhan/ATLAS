"""Tests for ai demo CLI subcommand (Sprint 50)."""

import json
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from app.cli import app


runner = CliRunner()


def test_demo_list_exit_code():
    result = runner.invoke(app, ["ai", "demo", "--project", "ATLAS", "--list"])
    assert result.exit_code == 0, result.output


def test_demo_list_shows_scenarios():
    result = runner.invoke(app, ["ai", "demo", "--project", "ATLAS", "--list"])
    assert result.exit_code == 0
    assert "chat_chrome_open" in result.output


def test_demo_list_json():
    result = runner.invoke(app, ["ai", "demo", "--project", "ATLAS", "--list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) >= 12
    ids = [s["scenario_id"] for s in data]
    assert "chat_chrome_open" in ids


def test_demo_scenario_chat_chrome_open():
    result = runner.invoke(app, ["ai", "demo", "--project", "ATLAS", "--scenario", "chat_chrome_open"])
    assert result.exit_code == 0
    assert "PASS" in result.output or "Scenario" in result.output


def test_demo_scenario_blocked_secret():
    result = runner.invoke(app, ["ai", "demo", "--project", "ATLAS", "--scenario", "blocked_secret"])
    assert result.exit_code == 0


def test_demo_category_voice():
    result = runner.invoke(
        app, ["ai", "demo", "--project", "ATLAS", "--category", "voice", "--show-safety"]
    )
    assert result.exit_code == 0


def test_demo_all_exit_code():
    result = runner.invoke(app, ["ai", "demo", "--project", "ATLAS", "--all"])
    assert result.exit_code == 0


def test_demo_all_json_valid():
    result = runner.invoke(app, ["ai", "demo", "--project", "ATLAS", "--all", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "total_scenarios" in data
    assert data["total_scenarios"] >= 12


def test_demo_all_show_safety():
    result = runner.invoke(
        app, ["ai", "demo", "--project", "ATLAS", "--all", "--show-safety"]
    )
    assert result.exit_code == 0
    assert "Safety" in result.output or "safety" in result.output.lower()


def test_demo_all_markdown_no_write():
    result = runner.invoke(
        app, ["ai", "demo", "--project", "ATLAS", "--all", "--markdown", "--no-write"]
    )
    assert result.exit_code == 0
    assert "ATLAS Sprint 50" in result.output or "Demo Report" in result.output


def test_demo_scenario_json():
    result = runner.invoke(
        app, ["ai", "demo", "--project", "ATLAS", "--scenario", "chat_chrome_open", "--json"]
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["scenario_id"] == "chat_chrome_open"
    assert "passed" in data
    assert "safety_flags" in data


def test_demo_output_path_inside_workspace(tmp_path):
    """Output path inside a temp workspace/outputs/demo dir should work."""
    out_dir = tmp_path / "workspace" / "outputs" / "demo"
    out_dir.mkdir(parents=True)
    out_file = out_dir / "test-demo.md"

    from app.demo.models import DemoReport
    from app.demo.report import write_report
    from app.demo.runner import DemoRunner

    demo_runner = DemoRunner(project_name="ATLAS")
    report = demo_runner.run_all()
    write_report(report, out_file, as_markdown=True)
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "ATLAS Sprint 50" in content


def test_demo_output_path_traversal_blocked(tmp_path):
    """Output path traversal outside workspace/outputs/demo should raise ValueError."""
    from app.demo.report import validate_output_path

    workspace_root = tmp_path
    bad_path = tmp_path / "etc" / "passwd"
    with pytest.raises(ValueError, match="workspace/outputs/demo"):
        validate_output_path(bad_path, workspace_root)


# --- Regression: existing ai commands still work ---

def test_ai_chat_still_works():
    result = runner.invoke(app, ["ai", "chat", "--project", "ATLAS", "Chrome'u aç"])
    assert result.exit_code == 0


def test_ai_voice_still_works():
    result = runner.invoke(
        app,
        ["ai", "voice", "--project", "ATLAS", "--mock-transcript", "Chrome'u aç"],
    )
    assert result.exit_code == 0


def test_ai_routine_still_works():
    result = runner.invoke(
        app, ["ai", "routine", "--project", "ATLAS", "Çalışma modunu başlat"]
    )
    assert result.exit_code == 0


def test_ai_reminder_still_works():
    result = runner.invoke(
        app,
        ["ai", "reminder", "--project", "ATLAS", "Bana 20 dakika sonra su içmeyi hatırlat"],
    )
    assert result.exit_code == 0


def test_ai_calendar_still_works():
    result = runner.invoke(
        app, ["ai", "calendar", "--project", "ATLAS", "Yarın 10'a toplantı ekle"]
    )
    assert result.exit_code == 0


def test_ai_panel_list_still_works():
    result = runner.invoke(app, ["ai", "panel", "--project", "ATLAS", "--list"])
    assert result.exit_code == 0
