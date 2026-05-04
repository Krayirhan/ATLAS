from __future__ import annotations

import json
import os

from typer.testing import CliRunner

from app.cli import app


def test_ai_main_mock_exit_zero() -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "main", "--project", "ATLAS", "--provider", "mock", "ATLAS şu an ne durumda?"],
        env=os.environ,
    )
    assert r.exit_code == 0, r.output


def test_ai_main_show_routing() -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "main", "--project", "ATLAS", "--provider", "mock", "--show-routing", "Sprint 34 için plan çıkar"],
        env=os.environ,
    )
    assert r.exit_code == 0, r.output
    assert "Routing" in r.output
    assert "planner-agent" in r.output


def test_ai_main_show_sources() -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "main", "--project", "ATLAS", "--provider", "mock", "--show-sources", "ATLAS şu an ne durumda?"],
        env=os.environ,
    )
    assert r.exit_code == 0, r.output
    assert "Sources" in r.output


def test_ai_main_json_output() -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "main", "--project", "ATLAS", "--provider", "mock", "--json", "AI layer güvenli mi?"],
        env=os.environ,
    )
    assert r.exit_code == 0, r.output
    data = json.loads(r.output)
    assert data["task_type"] in {"security_review", "code_review"}


def test_ai_main_approval_route_blocked() -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "main", "--project", "ATLAS", "--provider", "mock", "--show-routing", "git reset --hard güvenli mi?"],
        env=os.environ,
    )
    assert r.exit_code == 0, r.output
    assert "tool-approval-agent" in r.output
    assert "blocked" in r.output.lower()


def test_existing_ai_plan_review_and_approval_still_work() -> None:
    runner = CliRunner()
    r1 = runner.invoke(
        app,
        ["ai", "plan", "--project", "ATLAS", "--provider", "mock", "--goal", "Sprint 34 planla"],
        env=os.environ,
    )
    r2 = runner.invoke(
        app,
        ["ai", "review", "--project", "ATLAS", "--provider", "mock", "--scope", "safety"],
        env=os.environ,
    )
    r3 = runner.invoke(
        app,
        ["ai", "approval", "command", "--project", "ATLAS", "--cmd", "git push"],
        env=os.environ,
    )
    assert r1.exit_code == 0, r1.output
    assert r2.exit_code == 0, r2.output
    assert r3.exit_code == 0, r3.output
