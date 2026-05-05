"""Tests for DocumentationAgent — Sprint 35."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.agents.documentation_agent import DocumentationAgent
from app.agents.models import (
    AgentRunRequest,
    DocumentationAuditRequest,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_agent() -> DocumentationAgent:
    return DocumentationAgent()


def _make_request(scope: str = "all-light", provider: str = "mock") -> DocumentationAuditRequest:
    return DocumentationAuditRequest(
        project_name="ATLAS",
        scope=scope,
        provider=provider,
    )


# ---------------------------------------------------------------------------
# Capability / safety flags
# ---------------------------------------------------------------------------

class TestDocumentationAgentSafetyFlags:
    def test_read_only_true(self):
        agent = _make_agent()
        assert agent.read_only is True

    def test_can_write_files_false(self):
        agent = _make_agent()
        assert agent.can_write_files is False

    def test_can_run_commands_false(self):
        agent = _make_agent()
        assert agent.can_run_commands is False

    def test_can_call_tools_false(self):
        agent = _make_agent()
        assert agent.can_call_tools is False

    def test_agent_name(self):
        assert DocumentationAgent.agent_name == "documentation-agent"


# ---------------------------------------------------------------------------
# Scope support
# ---------------------------------------------------------------------------

class TestDocumentationAgentScopes:
    def test_all_light_scope(self):
        agent = _make_agent()
        result = agent.audit(_make_request("all-light"))
        assert result.scope == "all-light"
        assert result.decision in ("GO", "CONDITIONAL", "NO-GO")

    def test_readme_scope(self):
        agent = _make_agent()
        result = agent.audit(_make_request("readme"))
        assert result.scope == "readme"
        # source_checks only cover readme patterns
        labels = [sc.label for sc in result.source_checks]
        assert any("README" in label for label in labels)

    def test_notebooklm_scope(self):
        agent = _make_agent()
        result = agent.audit(_make_request("notebooklm"))
        assert result.scope == "notebooklm"
        labels = [sc.label for sc in result.source_checks]
        assert any("notebooklm" in label.lower() or "workflow" in label.lower() for label in labels)

    def test_agents_scope(self):
        agent = _make_agent()
        result = agent.audit(_make_request("agents"))
        assert result.scope == "agents"
        labels = [sc.label for sc in result.source_checks]
        # Should check sprint docs 14-21
        assert any("14" in label or "17" in label or "20" in label or "21" in label for label in labels)

    def test_roadmap_scope(self):
        agent = _make_agent()
        result = agent.audit(_make_request("roadmap"))
        assert result.scope == "roadmap"
        labels = [sc.label for sc in result.source_checks]
        assert any("06-next-sprints" in label or "07-v1-rc" in label for label in labels)

    def test_release_scope(self):
        agent = _make_agent()
        result = agent.audit(_make_request("release"))
        assert result.scope == "release"
        labels = [sc.label for sc in result.source_checks]
        assert any("07-v1-rc" in label or "05-release" in label for label in labels)

    def test_knowledge_base_scope(self):
        agent = _make_agent()
        result = agent.audit(_make_request("knowledge-base"))
        assert result.scope == "knowledge-base"

    def test_unknown_scope_raises(self):
        agent = _make_agent()
        from app.ai.context_loader import AIContextError
        with pytest.raises(AIContextError, match="Unknown documentation audit scope"):
            agent.audit(_make_request("invalid-scope"))


# ---------------------------------------------------------------------------
# Security / path safety
# ---------------------------------------------------------------------------

class TestDocumentationAgentSecurity:
    def test_does_not_read_env_files(self):
        agent = _make_agent()
        from pathlib import Path
        env_path = Path("E:/ATLAS/.env")
        assert not agent._is_allowed_path(env_path)

    def test_does_not_read_d_atlas(self):
        agent = _make_agent()
        from pathlib import Path
        d_path = Path("D:/ATLAS/README.md")
        assert not agent._is_allowed_path(d_path)

    def test_does_not_read_pem_files(self):
        agent = _make_agent()
        from pathlib import Path
        pem_path = Path("E:/ATLAS/some.pem")
        assert not agent._is_allowed_path(pem_path)

    def test_blocked_names(self):
        agent = _make_agent()
        from pathlib import Path
        for name in (".env", "id_rsa", "id_ed25519"):
            assert not agent._is_allowed_path(Path(f"E:/ATLAS/{name}"))

    def test_no_full_repo_scan(self):
        # _SCOPE_PATTERNS must use explicit paths only (no ** glob)
        for scope, patterns in DocumentationAgent._SCOPE_PATTERNS.items():
            for pattern in patterns:
                assert "**" not in pattern, f"Unbounded glob in scope {scope}: {pattern}"

    def test_result_does_not_write_files(self):
        # Audit result must not contain file write operations
        agent = _make_agent()
        result = agent.audit(_make_request("readme"))
        # The agent must be read_only — already tested above
        # Confirm result type is DocumentationAuditResult (not a write-operation type)
        from app.agents.models import DocumentationAuditResult
        assert isinstance(result, DocumentationAuditResult)

    def test_no_approval_token_in_result(self):
        agent = _make_agent()
        result = agent.audit(_make_request("readme"))
        assert "approval_token" not in result.metadata
        assert "prompt_logged" in result.metadata
        assert result.metadata["prompt_logged"] is False


# ---------------------------------------------------------------------------
# Bounds
# ---------------------------------------------------------------------------

class TestDocumentationAgentBounds:
    def test_max_files_respected(self):
        agent = _make_agent()
        result = agent.audit(DocumentationAuditRequest(
            project_name="ATLAS",
            scope="all-light",
            provider="mock",
            max_files=2,
        ))
        assert len(result.sources) <= 3  # allow report metadata source

    def test_max_chars_per_file_respected(self):
        agent = _make_agent()
        result = agent.audit(DocumentationAuditRequest(
            project_name="ATLAS",
            scope="readme",
            provider="mock",
            max_chars_per_file=100,
        ))
        for src in result.sources:
            assert src.char_count <= 100


# ---------------------------------------------------------------------------
# Structured output
# ---------------------------------------------------------------------------

class TestDocumentationAgentOutput:
    def test_returns_structured_findings(self):
        agent = _make_agent()
        result = agent.audit(_make_request("all-light"))
        from app.agents.models import DocumentationFinding
        for finding in result.findings:
            assert isinstance(finding, DocumentationFinding)
            assert finding.severity in ("critical", "high", "medium", "low", "info")

    def test_decision_valid_values(self):
        agent = _make_agent()
        result = agent.audit(_make_request("all-light"))
        assert result.decision in ("GO", "CONDITIONAL", "NO-GO")

    def test_source_metadata_returned(self):
        agent = _make_agent()
        result = agent.audit(_make_request("all-light", provider="mock"))
        assert isinstance(result.sources, list)
        assert result.metadata.get("provider") == "mock"

    def test_missing_docs_list(self):
        agent = _make_agent()
        result = agent.audit(_make_request("all-light"))
        assert isinstance(result.missing_docs, list)

    def test_recommendations_returned(self):
        agent = _make_agent()
        result = agent.audit(_make_request("all-light"))
        assert isinstance(result.recommendations, list)

    def test_roadmap_checks_returned(self):
        agent = _make_agent()
        result = agent.audit(_make_request("roadmap"))
        assert isinstance(result.roadmap_checks, list)

    def test_consistency_checks_returned(self):
        agent = _make_agent()
        result = agent.audit(_make_request("all-light"))
        assert isinstance(result.consistency_checks, list)


# ---------------------------------------------------------------------------
# BaseAgent.run() contract
# ---------------------------------------------------------------------------

class TestDocumentationAgentRunContract:
    def test_run_returns_agent_run_result(self):
        agent = _make_agent()
        from app.agents.models import AgentRunResult
        result = agent.run(AgentRunRequest(
            project_name="ATLAS",
            question="README guncel mi?",
            provider="mock",
        ))
        assert isinstance(result, AgentRunResult)
        assert result.agent_name == "documentation-agent"
        assert result.status in ("ok", "warning")


# ---------------------------------------------------------------------------
# Ollama provider (monkeypatched)
# ---------------------------------------------------------------------------

class TestDocumentationAgentOllama:
    def test_ollama_provider_monkeypatched(self):
        agent = _make_agent()
        mock_health = MagicMock()
        mock_health.ok = True
        mock_response = MagicMock()
        mock_response.text = "Mock Ollama documentation audit summary."

        with patch("app.agents.documentation_agent.OllamaAIProvider") as MockProvider:
            instance = MockProvider.return_value
            instance.health_check.return_value = mock_health
            instance.generate.return_value = mock_response

            result = agent.audit(_make_request("readme", provider="ollama"))
            assert result.decision in ("GO", "CONDITIONAL", "NO-GO")

    def test_ollama_timeout_graceful_warning(self):
        from app.ai.providers.base import AIProviderError
        agent = _make_agent()
        with patch("app.agents.documentation_agent.OllamaAIProvider") as MockProvider:
            instance = MockProvider.return_value
            instance.health_check.return_value = MagicMock(ok=False, message="timeout")
            result = agent.audit(_make_request("readme", provider="ollama"))
            assert any("timeout" in w.lower() for w in result.warnings)
            assert result.decision in ("GO", "CONDITIONAL", "NO-GO")
