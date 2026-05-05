from __future__ import annotations

import json
import os

from typer.testing import CliRunner

from app.cli import app


def test_ai_security_audit_all_light_exit_zero() -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "security-audit", "--project", "ATLAS", "--provider", "mock", "--scope", "all-light"],
        env=os.environ,
    )
    assert r.exit_code == 0, r.output
    assert "Decision" in r.output


def test_ai_security_audit_show_sources() -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "security-audit", "--project", "ATLAS", "--provider", "mock", "--scope", "agents", "--show-sources"],
        env=os.environ,
    )
    assert r.exit_code == 0, r.output
    assert "Sources" in r.output


def test_ai_security_audit_json_output() -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "security-audit", "--project", "ATLAS", "--provider", "mock", "--scope", "approval", "--json"],
        env=os.environ,
    )
    assert r.exit_code == 0, r.output
    data = json.loads(r.output)
    assert data["scope"] == "approval"
    assert data["decision"] in {"GO", "CONDITIONAL", "NO-GO"}


def test_ai_security_audit_unknown_scope_graceful_error() -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "security-audit", "--project", "ATLAS", "--provider", "mock", "--scope", "bad-scope"],
        env=os.environ,
    )
    assert r.exit_code == 1
    assert "Unknown security audit scope" in r.output


def test_ai_main_security_route_uses_security_auditor() -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "main", "--project", "ATLAS", "--provider", "mock", "--show-routing", "ATLAS guvenli mi?"],
        env=os.environ,
    )
    assert r.exit_code == 0, r.output
    assert "security-auditor-agent" in r.output


def test_existing_ai_main_still_works() -> None:
    r = CliRunner().invoke(
        app,
        ["ai", "main", "--project", "ATLAS", "--provider", "mock", "ATLAS su an ne durumda?"],
        env=os.environ,
    )
    assert r.exit_code == 0, r.output
