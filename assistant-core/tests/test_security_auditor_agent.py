from __future__ import annotations

from app.agents.models import SecurityAuditRequest
from app.agents.security_auditor_agent import SecurityAuditorAgent


def test_security_auditor_agent_read_only_flags() -> None:
    agent = SecurityAuditorAgent()
    assert agent.read_only is True
    assert agent.can_write_files is False
    assert agent.can_run_commands is False
    assert agent.can_call_tools is False


def test_security_auditor_agent_all_light_scope() -> None:
    result = SecurityAuditorAgent().audit(SecurityAuditRequest(project_name="ATLAS", scope="all-light", provider="mock"))
    assert result.scope == "all-light"
    assert result.sources
    assert result.decision in {"GO", "CONDITIONAL", "NO-GO"}
    assert result.summary


def test_security_auditor_agent_agents_scope_checks_capabilities() -> None:
    result = SecurityAuditorAgent().audit(SecurityAuditRequest(project_name="ATLAS", scope="agents", provider="mock"))
    assert result.agent_capabilities
    assert all(item.read_only for item in result.agent_capabilities)
    assert all(item.can_write_files is False for item in result.agent_capabilities)
    assert all(item.can_run_commands is False for item in result.agent_capabilities)
    assert all(item.can_call_tools is False for item in result.agent_capabilities)


def test_security_auditor_agent_mcp_scope_no_blocked_sources() -> None:
    result = SecurityAuditorAgent().audit(SecurityAuditRequest(project_name="ATLAS", scope="mcp", provider="mock"))
    assert result.mcp_exposure
    assert all("D:\\ATLAS" not in source.path for source in result.sources)


def test_security_auditor_agent_approval_scope_checks_canonical_commands() -> None:
    result = SecurityAuditorAgent().audit(SecurityAuditRequest(project_name="ATLAS", scope="approval", provider="mock"))
    statuses = {item.check_name: item.status for item in result.approval_policy}
    assert "git reset --hard" in statuses
    assert "git push" in statuses
    assert "python -m app.cli doctor --full" in statuses


def test_security_auditor_agent_context_scope_returns_structured_findings() -> None:
    result = SecurityAuditorAgent().audit(SecurityAuditRequest(project_name="ATLAS", scope="context", provider="mock"))
    assert isinstance(result.findings, list)
    assert all(".env" not in source.path.lower() for source in result.sources)


def test_security_auditor_agent_unknown_scope_graceful_error() -> None:
    agent = SecurityAuditorAgent()
    try:
        agent.audit(SecurityAuditRequest(project_name="ATLAS", scope="invalid-scope"))  # type: ignore[arg-type]
    except Exception as exc:  # noqa: BLE001
        assert "Unknown security audit scope" in str(exc)
    else:
        raise AssertionError("Expected unknown scope error")


def test_security_auditor_agent_max_files_and_chars_limits() -> None:
    result = SecurityAuditorAgent().audit(
        SecurityAuditRequest(project_name="ATLAS", scope="all-light", provider="mock", max_files=2, max_chars_per_file=120)
    )
    assert len(result.sources) <= 3
    file_sources = [source for source in result.sources if source.source_type == "security-audit-file"]
    assert all(source.char_count <= 120 for source in file_sources)


def test_security_auditor_agent_ollama_warning_graceful(monkeypatch) -> None:
    agent = SecurityAuditorAgent()

    def _raise(*_args, **_kwargs):
        from app.ai.providers.base import AIProviderError

        raise AIProviderError("timeout")

    monkeypatch.setattr(agent, "_ollama_summary", _raise)
    result = agent.audit(SecurityAuditRequest(project_name="ATLAS", scope="context", provider="ollama"))
    assert result.status == "warning"
    assert "timeout" in "\n".join(result.warnings)


def test_security_auditor_agent_source_metadata_present() -> None:
    result = SecurityAuditorAgent().audit(SecurityAuditRequest(project_name="ATLAS", scope="docs", provider="mock"))
    assert result.sources
    assert all(source.char_count >= 0 for source in result.sources)
    assert all("scope" in source.metadata or source.metadata.get("path_only") for source in result.sources)
