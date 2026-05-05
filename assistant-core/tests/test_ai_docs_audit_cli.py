"""CLI integration tests for ai docs-audit command — Sprint 35."""

from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from app.cli import app


runner = CliRunner()


# ---------------------------------------------------------------------------
# Basic invocation
# ---------------------------------------------------------------------------

class TestAiDocsAuditCLI:
    def test_all_light_exit_zero(self):
        result = runner.invoke(app, [
            "ai", "docs-audit",
            "--project", "ATLAS",
            "--provider", "mock",
            "--scope", "all-light",
        ])
        assert result.exit_code == 0, result.output

    def test_readme_scope_exit_zero(self):
        result = runner.invoke(app, [
            "ai", "docs-audit",
            "--project", "ATLAS",
            "--provider", "mock",
            "--scope", "readme",
        ])
        assert result.exit_code == 0, result.output

    def test_notebooklm_scope_exit_zero(self):
        result = runner.invoke(app, [
            "ai", "docs-audit",
            "--project", "ATLAS",
            "--provider", "mock",
            "--scope", "notebooklm",
        ])
        assert result.exit_code == 0, result.output

    def test_agents_scope_exit_zero(self):
        result = runner.invoke(app, [
            "ai", "docs-audit",
            "--project", "ATLAS",
            "--provider", "mock",
            "--scope", "agents",
        ])
        assert result.exit_code == 0, result.output

    def test_roadmap_scope_exit_zero(self):
        result = runner.invoke(app, [
            "ai", "docs-audit",
            "--project", "ATLAS",
            "--provider", "mock",
            "--scope", "roadmap",
        ])
        assert result.exit_code == 0, result.output

    def test_release_scope_exit_zero(self):
        result = runner.invoke(app, [
            "ai", "docs-audit",
            "--project", "ATLAS",
            "--provider", "mock",
            "--scope", "release",
        ])
        assert result.exit_code == 0, result.output

    def test_knowledge_base_scope_exit_zero(self):
        result = runner.invoke(app, [
            "ai", "docs-audit",
            "--project", "ATLAS",
            "--provider", "mock",
            "--scope", "knowledge-base",
        ])
        assert result.exit_code == 0, result.output


# ---------------------------------------------------------------------------
# --show-sources
# ---------------------------------------------------------------------------

class TestDocsAuditShowSources:
    def test_show_sources_readme(self):
        result = runner.invoke(app, [
            "ai", "docs-audit",
            "--project", "ATLAS",
            "--provider", "mock",
            "--scope", "readme",
            "--show-sources",
        ])
        assert result.exit_code == 0
        assert "Sources" in result.output or "documentation-audit-file" in result.output


# ---------------------------------------------------------------------------
# --json output
# ---------------------------------------------------------------------------

class TestDocsAuditJson:
    def test_json_output_valid(self):
        result = runner.invoke(app, [
            "ai", "docs-audit",
            "--project", "ATLAS",
            "--provider", "mock",
            "--scope", "all-light",
            "--json",
        ])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert "decision" in data
        assert data["decision"] in ("GO", "CONDITIONAL", "NO-GO")
        assert "findings" in data
        assert "scope" in data
        assert data["scope"] == "all-light"

    def test_json_has_source_checks(self):
        result = runner.invoke(app, [
            "ai", "docs-audit",
            "--project", "ATLAS",
            "--provider", "mock",
            "--scope", "readme",
            "--json",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "source_checks" in data
        assert isinstance(data["source_checks"], list)

    def test_json_has_recommendations(self):
        result = runner.invoke(app, [
            "ai", "docs-audit",
            "--project", "ATLAS",
            "--provider", "mock",
            "--scope", "all-light",
            "--json",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "recommendations" in data


# ---------------------------------------------------------------------------
# Unknown scope
# ---------------------------------------------------------------------------

class TestDocsAuditUnknownScope:
    def test_unknown_scope_nonzero_exit(self):
        result = runner.invoke(app, [
            "ai", "docs-audit",
            "--project", "ATLAS",
            "--provider", "mock",
            "--scope", "invalid-xyz",
        ])
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# Existing commands not broken
# ---------------------------------------------------------------------------

class TestExistingCommandsIntact:
    def test_ai_main_not_broken(self):
        result = runner.invoke(app, [
            "ai", "main",
            "--project", "ATLAS",
            "--provider", "mock",
            "ATLAS su an ne durumda?",
        ])
        assert result.exit_code == 0, result.output

    def test_ai_security_audit_not_broken(self):
        result = runner.invoke(app, [
            "ai", "security-audit",
            "--project", "ATLAS",
            "--provider", "mock",
            "--scope", "all-light",
        ])
        assert result.exit_code == 0, result.output


# ---------------------------------------------------------------------------
# Documentation question routing via ai main
# ---------------------------------------------------------------------------

class TestDocumentationRouteViaMainAgent:
    def test_readme_question_routes_to_documentation_agent(self):
        result = runner.invoke(app, [
            "ai", "main",
            "--project", "ATLAS",
            "--provider", "mock",
            "--show-routing",
            "README guncel mi?",
        ])
        assert result.exit_code == 0, result.output
        # Should show documentation-agent in routing
        assert "documentation-agent" in result.output or "documentation_question" in result.output

    def test_notebooklm_question_routes_to_documentation_agent(self):
        result = runner.invoke(app, [
            "ai", "main",
            "--project", "ATLAS",
            "--provider", "mock",
            "--show-routing",
            "NotebookLM workflow eksik mi?",
        ])
        assert result.exit_code == 0, result.output
        assert "documentation-agent" in result.output or "documentation_question" in result.output

    def test_roadmap_question_routes_to_documentation_agent(self):
        result = runner.invoke(app, [
            "ai", "main",
            "--project", "ATLAS",
            "--provider", "mock",
            "--show-routing",
            "Roadmap dogru mu?",
        ])
        assert result.exit_code == 0, result.output
        assert "documentation-agent" in result.output or "documentation_question" in result.output

    def test_security_route_not_broken(self):
        result = runner.invoke(app, [
            "ai", "main",
            "--project", "ATLAS",
            "--provider", "mock",
            "--show-routing",
            "ATLAS guvenli mi?",
        ])
        assert result.exit_code == 0, result.output
        assert "security-auditor-agent" in result.output or "security_review" in result.output

    def test_plan_route_not_broken(self):
        result = runner.invoke(app, [
            "ai", "main",
            "--project", "ATLAS",
            "--provider", "mock",
            "--show-routing",
            "Sprint planla",
        ])
        assert result.exit_code == 0, result.output
        assert "planner-agent" in result.output or "sprint_plan" in result.output


# ---------------------------------------------------------------------------
# Security tests via CLI
# ---------------------------------------------------------------------------

class TestDocsAuditSecurityCLI:
    def test_no_approval_token_in_json_output(self):
        result = runner.invoke(app, [
            "ai", "docs-audit",
            "--project", "ATLAS",
            "--provider", "mock",
            "--scope", "all-light",
            "--json",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "approval_token" not in data
        assert data["metadata"].get("prompt_logged") is False

    def test_prompt_not_logged_in_metadata(self):
        result = runner.invoke(app, [
            "ai", "docs-audit",
            "--project", "ATLAS",
            "--provider", "mock",
            "--scope", "readme",
            "--json",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["metadata"].get("prompt_logged") is False
