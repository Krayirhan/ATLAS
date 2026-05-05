from __future__ import annotations

from app.agents.main_agent import MainAgent
from app.agents.models import MainAgentRequest


def test_main_agent_read_only_flags() -> None:
    agent = MainAgent()
    assert agent.read_only is True
    assert agent.can_write_files is False
    assert agent.can_run_commands is False
    assert agent.can_call_tools is False


def test_main_agent_project_question_route() -> None:
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="ATLAS su an ne durumda?", provider="mock"))
    assert result.task_type in {"project_status", "project_question"}
    assert "project-qa-agent" in result.route.selected_agents


def test_main_agent_sprint_plan_route() -> None:
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="Sprint 34 icin plan cikar", provider="mock"))
    assert result.task_type == "sprint_plan"
    assert "planner-agent" in result.route.selected_agents


def test_main_agent_review_route() -> None:
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="AI layer'i incele", provider="mock"))
    assert result.task_type == "code_review"
    assert "code-reviewer-agent" in result.route.selected_agents


def test_main_agent_security_audit_route() -> None:
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="ATLAS guvenli mi?", provider="mock"))
    assert result.task_type == "security_review"
    assert "security-auditor-agent" in result.route.selected_agents


def test_main_agent_approval_route() -> None:
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="git reset --hard guvenli mi?", provider="mock"))
    assert result.task_type == "approval_check"
    assert "tool-approval-agent" in result.route.selected_agents
    assert "blocked" in result.answer.lower()


def test_main_agent_unknown_route_graceful() -> None:
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="Bana bir sey soyle", provider="mock"))
    assert result.task_type in {"unknown", "project_question", "project_status"}
    assert result.answer


def test_main_agent_apply_request_does_not_execute() -> None:
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="git push yap", provider="mock"))
    assert result.task_type == "approval_check"
    assert "not executed" in result.answer.lower() or "preview" in result.answer.lower()


def test_main_agent_source_list_and_routing_metadata() -> None:
    result = MainAgent().handle(
        MainAgentRequest(project_name="ATLAS", user_message="ATLAS su an ne durumda?", provider="mock", show_sources=True, show_routing=True)
    )
    assert result.sources
    assert "route" in result.metadata
    assert "steps" in result.metadata


def test_main_agent_ollama_warning_graceful(monkeypatch) -> None:
    agent = MainAgent()

    def _raise(*_args, **_kwargs):
        from app.ai.providers.base import AIProviderError

        raise AIProviderError("timeout")

    monkeypatch.setattr(agent._qa_agent, "answer", _raise)
    result = agent.handle(MainAgentRequest(project_name="ATLAS", user_message="ATLAS su an ne durumda?", provider="ollama"))
    assert result.response_mode == "refusal_or_warning"
    assert "timeout" in "\n".join(result.warnings)


# ---------------------------------------------------------------------------
# Sprint 34.1 — Security routing fix tests
# ---------------------------------------------------------------------------


def test_normalize_tr() -> None:
    """_normalize_tr converts Turkish diacritics to ASCII."""
    agent = MainAgent()
    assert agent._normalize_tr("üniçode güvenlik") == "unicode guvenlik"
    assert agent._normalize_tr("güvenli mi") == "guvenli mi"
    assert agent._normalize_tr("öğşçıü") == "ogscıu".replace("ı", "i")
    assert agent._normalize_tr("ascii only") == "ascii only"


def test_security_route_atlas_guvenli_mi_with_diacritics() -> None:
    """'ATLAS güvenli mi?' (with ü) must route to SecurityAuditorAgent."""
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="ATLAS güvenli mi?", provider="mock"))
    assert result.task_type == "security_review", f"Expected security_review, got {result.task_type}"
    assert "security-auditor-agent" in result.route.selected_agents


def test_security_route_mcp_config_guvenli_mi() -> None:
    """'MCP config güvenli mi?' must route to SecurityAuditorAgent."""
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="MCP config güvenli mi?", provider="mock"))
    assert result.task_type == "security_review"
    assert "security-auditor-agent" in result.route.selected_agents


def test_security_route_mcp_guvenli_mi() -> None:
    """'MCP güvenli mi?' (short form) must route to SecurityAuditorAgent."""
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="MCP güvenli mi?", provider="mock"))
    assert result.task_type == "security_review"
    assert "security-auditor-agent" in result.route.selected_agents


def test_security_route_yazma_yetkisi() -> None:
    """'Agentlarda yazma yetkisi açılmış mı?' must route to SecurityAuditorAgent."""
    result = MainAgent().handle(
        MainAgentRequest(project_name="ATLAS", user_message="Agentlarda yazma yetkisi açılmış mı?", provider="mock")
    )
    assert result.task_type == "security_review"
    assert "security-auditor-agent" in result.route.selected_agents


def test_security_route_d_atlas_kalintisi() -> None:
    r"""'D:\ATLAS kalıntısı var mı?' must route to SecurityAuditorAgent."""
    result = MainAgent().handle(
        MainAgentRequest(project_name="ATLAS", user_message=r"D:\ATLAS kalıntısı var mı?", provider="mock")
    )
    assert result.task_type == "security_review"
    assert "security-auditor-agent" in result.route.selected_agents


def test_security_route_guvenlik_keyword() -> None:
    """A message containing 'güvenlik' alone must route to SecurityAuditorAgent."""
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="ATLAS güvenlik durumu nedir?", provider="mock"))
    assert result.task_type == "security_review"
    assert "security-auditor-agent" in result.route.selected_agents


# ---------------------------------------------------------------------------
# Sprint 34.1 — Regression: existing routes must remain intact
# ---------------------------------------------------------------------------


def test_regression_git_reset_still_approval() -> None:
    """'git reset --hard güvenli mi?' must still go to ToolApprovalAgent."""
    result = MainAgent().handle(
        MainAgentRequest(project_name="ATLAS", user_message="git reset --hard güvenli mi?", provider="mock")
    )
    assert result.task_type == "approval_check"
    assert "tool-approval-agent" in result.route.selected_agents


def test_regression_sprint_plan_still_planner() -> None:
    """Sprint plan questions must still route to PlannerAgent."""
    result = MainAgent().handle(
        MainAgentRequest(project_name="ATLAS", user_message="Sprint 35 için plan çıkar", provider="mock")
    )
    assert result.task_type == "sprint_plan"
    assert "planner-agent" in result.route.selected_agents


def test_regression_project_status_still_qa() -> None:
    """Project status questions must still route to ProjectQAAgent."""
    result = MainAgent().handle(
        MainAgentRequest(project_name="ATLAS", user_message="ATLAS su an ne durumda?", provider="mock")
    )
    assert result.task_type in {"project_status", "project_question"}
    assert "project-qa-agent" in result.route.selected_agents

