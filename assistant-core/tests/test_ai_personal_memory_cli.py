import json
from typer.testing import CliRunner
from app.cli import app

runner = CliRunner()

def test_cli_ai_memory_remember():
    result = runner.invoke(app, ["ai", "memory-personal", "--project", "ATLAS", "Bunu hatırla: Chrome kullanırım"])
    assert result.exit_code == 0
    assert "SUCCESS" in result.stdout

def test_cli_ai_memory_blocked():
    result = runner.invoke(app, ["ai", "memory-personal", "--project", "ATLAS", "Şifremin 1234 olduğunu hatırla"])
    assert result.exit_code == 0
    assert "BLOCKED" in result.stdout

def test_cli_ai_memory_json():
    result = runner.invoke(app, ["ai", "memory-personal", "--project", "ATLAS", "--json", "Neleri hatırlıyorsun?"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["status"] == "shown"

def test_cli_ai_memory_clear():
    result = runner.invoke(app, ["ai", "memory-personal", "--project", "ATLAS", "--clear", "dummy"])
    assert result.exit_code == 0
    assert "temizlendi" in result.stdout.lower() or "clear" in result.stdout.lower()
