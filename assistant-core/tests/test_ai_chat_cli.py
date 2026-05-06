import pytest
import json
from typer.testing import CliRunner
from app.cli import app

runner = CliRunner()

def test_cli_ai_chat_chrome():
    result = runner.invoke(app, ["ai", "chat", "--project", "ATLAS", "Chrome'u aç"])
    assert result.exit_code == 0
    assert "ATLAS" in result.stdout

def test_cli_ai_chat_clarification():
    result = runner.invoke(app, ["ai", "chat", "--project", "ATLAS", "Işığı aç"])
    assert result.exit_code == 0
    assert "Hangi" in result.stdout

def test_cli_ai_chat_blocked():
    result = runner.invoke(app, ["ai", "chat", "--project", "ATLAS", "Şifrelerimi oku"])
    assert result.exit_code == 0
    assert "engellendi" in result.stdout

def test_cli_ai_chat_json():
    result = runner.invoke(app, ["ai", "chat", "--project", "ATLAS", "--json", "abc"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["response_type"] == "clarification"

def test_cli_ai_chat_show_state():
    result = runner.invoke(app, ["ai", "chat", "--project", "ATLAS", "--show-state", "Chrome'u aç"])
    assert result.exit_code == 0
    assert "State: intent=" in result.stdout
