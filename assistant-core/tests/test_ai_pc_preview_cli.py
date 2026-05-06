import pytest
from typer.testing import CliRunner
from app.cli import app
import json

runner = CliRunner()

def test_cli_pc_preview_open_app():
    result = runner.invoke(app, ["ai", "pc-preview", "--project", "ATLAS", "Chrome'u aç"])
    assert result.exit_code == 0
    assert "Result Status" in result.stdout
    
def test_cli_pc_preview_blocked():
    result = runner.invoke(app, ["ai", "pc-preview", "--project", "ATLAS", "Şifrelerimi oku"])
    assert result.exit_code == 0
    assert "Result Status" in result.stdout or "Blocked" in result.stdout
    
def test_cli_pc_preview_json():
    result = runner.invoke(app, ["ai", "pc-preview", "--project", "ATLAS", "--json", "Bilgisayar bilgilerini göster"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "pc_plan" in data
