import json

from typer.testing import CliRunner

from app.cli import app


runner = CliRunner()


def test_cli_ai_routine_list():
    result = runner.invoke(app, ["ai", "routine", "--project", "ATLAS", "--list"])
    assert result.exit_code == 0
    assert "Çalışma Modu" in result.stdout


def test_cli_ai_routine_run():
    result = runner.invoke(app, ["ai", "routine", "--project", "ATLAS", "Çalışma modunu başlat"])
    assert result.exit_code == 0
    assert "CONFIRMATION REQUIRED" in result.stdout


def test_cli_ai_routine_show_preview():
    result = runner.invoke(app, ["ai", "routine", "--project", "ATLAS", "--show-preview", "Uyku modunu başlat"])
    assert result.exit_code == 0
    assert "Routine Preview" in result.stdout
    assert "Conf Req: True" in result.stdout


def test_cli_ai_routine_json():
    result = runner.invoke(app, ["ai", "routine", "--project", "ATLAS", "--json", "Evden çıkıyorum"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["status"] == "awaiting_confirmation"
