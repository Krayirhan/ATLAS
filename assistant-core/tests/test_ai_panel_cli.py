import json
import os

from typer.testing import CliRunner

from app.cli import app


def test_ai_panel_submit_and_list(tmp_path) -> None:
    store_path = tmp_path / "panel.json"
    env = {**os.environ, "ATLAS_PANEL_STORE_PATH": str(store_path)}
    runner = CliRunner()

    submit = runner.invoke(app, ["ai", "panel", "--project", "ATLAS", "--submit", "Salon isigini ac"], env=env)
    assert submit.exit_code == 0, submit.output
    assert "created" in submit.output.lower()

    listed = runner.invoke(app, ["ai", "panel", "--project", "ATLAS", "--list"], env=env)
    assert listed.exit_code == 0, listed.output
    assert "panel-" in listed.output


def test_ai_panel_submit_clarification_and_blocked(tmp_path) -> None:
    store_path = tmp_path / "panel.json"
    env = {**os.environ, "ATLAS_PANEL_STORE_PATH": str(store_path)}
    runner = CliRunner()

    clarification = runner.invoke(app, ["ai", "panel", "--project", "ATLAS", "--submit", "Isigi ac"], env=env)
    assert clarification.exit_code == 0, clarification.output
    assert "clarification_required" in clarification.output

    blocked = runner.invoke(app, ["ai", "panel", "--project", "ATLAS", "--submit", "Sifrelerimi oku"], env=env)
    assert blocked.exit_code == 0, blocked.output
    assert "blocked" in blocked.output.lower()


def test_ai_panel_json_list(tmp_path) -> None:
    store_path = tmp_path / "panel.json"
    env = {**os.environ, "ATLAS_PANEL_STORE_PATH": str(store_path)}
    runner = CliRunner()
    runner.invoke(app, ["ai", "panel", "--project", "ATLAS", "--submit", "Chrome'u ac"], env=env)
    result = runner.invoke(app, ["ai", "panel", "--project", "ATLAS", "--json", "--list"], env=env)
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "listed"
    assert len(payload["items"]) == 1


def test_ai_panel_approve_deny_cancel(tmp_path) -> None:
    store_path = tmp_path / "panel.json"
    env = {**os.environ, "ATLAS_PANEL_STORE_PATH": str(store_path)}
    runner = CliRunner()

    created = runner.invoke(app, ["ai", "panel", "--project", "ATLAS", "--json", "--submit", "Salon isigini ac"], env=env)
    payload = json.loads(created.output)
    item_id = payload["item"]["item_id"]

    approved = runner.invoke(app, ["ai", "panel", "--project", "ATLAS", "--approve", item_id], env=env)
    assert approved.exit_code == 0, approved.output
    assert "approved" in approved.output.lower()

    created_2 = runner.invoke(app, ["ai", "panel", "--project", "ATLAS", "--json", "--submit", "Chrome'u ac"], env=env)
    item_id_2 = json.loads(created_2.output)["item"]["item_id"]
    denied = runner.invoke(app, ["ai", "panel", "--project", "ATLAS", "--deny", item_id_2], env=env)
    assert denied.exit_code == 0, denied.output
    assert "denied" in denied.output.lower()

    created_3 = runner.invoke(app, ["ai", "panel", "--project", "ATLAS", "--json", "--submit", "Salon isigini ac"], env=env)
    item_id_3 = json.loads(created_3.output)["item"]["item_id"]
    cancelled = runner.invoke(app, ["ai", "panel", "--project", "ATLAS", "--cancel", item_id_3], env=env)
    assert cancelled.exit_code == 0, cancelled.output
    assert "cancelled" in cancelled.output.lower()
