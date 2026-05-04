from __future__ import annotations

from app.agents.tool_approval_agent import ToolApprovalAgent
from app.approval.models import ProposedCommand


def test_tool_approval_agent_read_only_flags() -> None:
    agent = ToolApprovalAgent()
    assert agent.read_only is True
    assert agent.can_write_files is False
    assert agent.can_run_commands is False
    assert agent.can_call_tools is False


def test_tool_approval_agent_blocked_command() -> None:
    decision = ToolApprovalAgent().evaluate_command(
        ProposedCommand(project_name="ATLAS", command="git reset --hard", source_agent="planner-agent")
    )
    assert decision.status == "blocked"
    assert decision.blocked is True


def test_tool_approval_agent_approval_required_command() -> None:
    decision = ToolApprovalAgent().evaluate_command(
        ProposedCommand(project_name="ATLAS", command="git push", source_agent="planner-agent")
    )
    assert decision.status == "approval_required"
    assert decision.approval_required is True


def test_tool_approval_agent_safe_readonly_command() -> None:
    decision = ToolApprovalAgent().evaluate_command(
        ProposedCommand(project_name="ATLAS", command="python -m app.cli ai memory --project ATLAS", source_agent="planner-agent")
    )
    assert decision.status == "safe_readonly"


def test_tool_approval_agent_audit_metadata_has_no_secrets() -> None:
    decision = ToolApprovalAgent().evaluate_command(
        ProposedCommand(
            project_name="ATLAS",
            command="python -m app.cli doctor --full",
            reason="check",
            source_agent="planner-agent",
            user_goal="validate runtime",
        )
    )
    metadata_text = str(decision.audit_metadata).lower()
    assert "secret" not in metadata_text
    assert "token" not in metadata_text
    assert "doctor --full" not in metadata_text
