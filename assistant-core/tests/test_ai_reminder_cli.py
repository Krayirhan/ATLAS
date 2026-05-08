import json

from typer.testing import CliRunner

from app.cli import app
import app.personal_assistant.store as personal_assistant_store


def test_ai_reminder_create_exit_code_zero(tmp_path, monkeypatch) -> None:
    store_path = tmp_path / "personal-assistant.json"
    monkeypatch.setattr(personal_assistant_store, "_default_store_path", lambda: store_path)
    personal_assistant_store._global_store = None
    result = CliRunner().invoke(
        app,
        ["ai", "reminder", "--project", "ATLAS", "Bana 20 dakika sonra su icmeyi hatirlat"],
    )
    assert result.exit_code == 0, result.output
    assert "onay gerekiyor" in result.output.lower()
    assert "hatırlatıcı" in result.output.lower()


def test_ai_reminder_list_exit_code_zero(tmp_path, monkeypatch) -> None:
    store_path = tmp_path / "personal-assistant.json"
    monkeypatch.setattr(personal_assistant_store, "_default_store_path", lambda: store_path)
    personal_assistant_store._global_store = None
    runner = CliRunner()
    runner.invoke(app, ["ai", "reminder", "--project", "ATLAS", "Bana 20 dakika sonra su icmeyi hatirlat"])
    result = runner.invoke(app, ["ai", "reminder", "--project", "ATLAS", "--list"])
    assert result.exit_code == 0, result.output
    assert "Hatırlatıcı taslakları:" in result.output


def test_ai_reminder_json_outputs_valid_json(tmp_path, monkeypatch) -> None:
    store_path = tmp_path / "personal-assistant.json"
    monkeypatch.setattr(personal_assistant_store, "_default_store_path", lambda: store_path)
    personal_assistant_store._global_store = None
    result = CliRunner().invoke(
        app,
        ["ai", "reminder", "--project", "ATLAS", "--json", "Yarin 9da toplantiyi hatirlat"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "pending_confirmation"
