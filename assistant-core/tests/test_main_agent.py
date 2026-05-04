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
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="ATLAS şu an ne durumda?", provider="mock"))
    assert result.task_type in {"project_status", "project_question"}
    assert "project-qa-agent" in result.route.selected_agents


def test_main_agent_sprint_plan_route() -> None:
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="Sprint 34 için plan çıkar", provider="mock"))
    assert result.task_type == "sprint_plan"
    assert "planner-agent" in result.route.selected_agents


def test_main_agent_review_route() -> None:
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="AI layer güvenli mi?", provider="mock"))
    assert result.task_type in {"security_review", "code_review"}
    assert "code-reviewer-agent" in result.route.selected_agents


def test_main_agent_approval_route() -> None:
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="git reset --hard güvenli mi?", provider="mock"))
    assert result.task_type == "approval_check"
    assert "tool-approval-agent" in result.route.selected_agents
    assert "blocked" in result.answer.lower()


def test_main_agent_unknown_route_graceful() -> None:
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="Bana bir şey söyle", provider="mock"))
    assert result.task_type in {"unknown", "project_question", "project_status"}
    assert result.answer


def test_main_agent_apply_request_does_not_execute() -> None:
    result = MainAgent().handle(MainAgentRequest(project_name="ATLAS", user_message="git push yap", provider="mock"))
    assert result.task_type == "approval_check"
    assert "not executed" in result.answer.lower() or "preview" in result.answer.lower()


def test_main_agent_source_list_and_routing_metadata() -> None:
    result = MainAgent().handle(
        MainAgentRequest(project_name="ATLAS", user_message="ATLAS şu an ne durumda?", provider="mock", show_sources=True, show_routing=True)
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
    result = agent.handle(MainAgentRequest(project_name="ATLAS", user_message="ATLAS şu an ne durumda?", provider="ollama"))
    assert result.response_mode == "refusal_or_warning"
    assert "timeout" in "\n".join(result.warnings)
