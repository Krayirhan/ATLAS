import json

from typer.testing import CliRunner

from app.cli import app
import app.personal_assistant.store as personal_assistant_store


def test_ai_calendar_query_exit_code_zero(tmp_path, monkeypatch) -> None:
    store_path = tmp_path / "personal-assistant.json"
    monkeypatch.setattr(personal_assistant_store, "_default_store_path", lambda: store_path)
    personal_assistant_store._global_store = None
    result = CliRunner().invoke(
        app,
        ["ai", "calendar", "--project", "ATLAS", "Bugun takvimimde ne var?"],
    )
    assert result.exit_code == 0, result.output
    assert "Takvim önizlemesi" in result.output


def test_ai_calendar_draft_exit_code_zero(tmp_path, monkeypatch) -> None:
    store_path = tmp_path / "personal-assistant.json"
    monkeypatch.setattr(personal_assistant_store, "_default_store_path", lambda: store_path)
    personal_assistant_store._global_store = None
    result = CliRunner().invoke(
        app,
        ["ai", "calendar", "--project", "ATLAS", "Yarin 10a toplanti ekle"],
    )
    assert result.exit_code == 0, result.output
    assert "onay gerekiyor" in result.output.lower()
    assert "takvim taslağı" in result.output.lower()


def test_ai_calendar_json_outputs_valid_json(tmp_path, monkeypatch) -> None:
    store_path = tmp_path / "personal-assistant.json"
    monkeypatch.setattr(personal_assistant_store, "_default_store_path", lambda: store_path)
    personal_assistant_store._global_store = None
    result = CliRunner().invoke(
        app,
        ["ai", "calendar", "--project", "ATLAS", "--json", "Cuma 14:00e gorusme koy"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "pending_confirmation"
