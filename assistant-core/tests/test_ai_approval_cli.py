from __future__ import annotations

import json
import os

from typer.testing import CliRunner

from app.cli import app


def test_ai_approval_blocked_exit_zero() -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "approval", "command", "--project", "ATLAS", "--cmd", "git reset --hard"],
        env=os.environ,
    )
    assert r.exit_code == 0, r.output
    assert "blocked" in r.output.lower()


def test_ai_approval_git_push_requires_approval() -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "approval", "command", "--project", "ATLAS", "--cmd", "git push"],
        env=os.environ,
    )
    assert r.exit_code == 0, r.output
    assert "approval_required" in r.output.lower()


def test_ai_approval_doctor_preview_or_safe() -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "approval", "command", "--project", "ATLAS", "--cmd", "python -m app.cli doctor --full"],
        env=os.environ,
    )
    assert r.exit_code == 0, r.output
    assert ("preview_allowed" in r.output.lower()) or ("safe_readonly" in r.output.lower())
    assert "not executed" in r.output.lower()


def test_ai_approval_json_output() -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "approval", "command", "--project", "ATLAS", "--cmd", "python -m app.cli doctor --full", "--json"],
        env=os.environ,
    )
    assert r.exit_code == 0, r.output
    data = json.loads(r.output)
    assert data["status"] in {"preview_allowed", "safe_readonly"}


def test_existing_ai_plan_and_review_still_work() -> None:
    runner = CliRunner()
    r1 = runner.invoke(
        app,
        ["ai", "plan", "--project", "ATLAS", "--provider", "mock", "--goal", "Sprint 33 için MainAgent Alpha planla"],
        env=os.environ,
    )
    r2 = runner.invoke(
        app,
        ["ai", "review", "--project", "ATLAS", "--provider", "mock", "--scope", "safety"],
        env=os.environ,
    )
    assert r1.exit_code == 0, r1.output
    assert r2.exit_code == 0, r2.output
