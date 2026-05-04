"""ToolApprovalAgent: preview-only decision layer for proposed actions."""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.agents.models import AgentRunRequest, AgentRunResult
from app.approval.evaluator import ApprovalEvaluator
from app.approval.models import ApprovalDecision, ProposedAction, ProposedCommand
from app.logging.audit import write_audit
from app.paths import get_logs_dir


class ToolApprovalAgent(BaseAgent):
    agent_name = "tool-approval-agent"

    def __init__(self, *, evaluator: ApprovalEvaluator | None = None) -> None:
        self._evaluator = evaluator or ApprovalEvaluator()

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        decision = self.evaluate_command(
            ProposedCommand(
                project_name=request.project_name,
                command=request.question,
                source_agent=request.provider or "",
            )
        )
        return AgentRunResult(
            agent_name=self.agent_name,
            project_name=request.project_name,
            status=decision.status,
            answer=self._format_decision(decision),
            sources=[],
            warnings=[],
            metadata=decision.audit_metadata,
        )

    def evaluate(self, action: ProposedAction) -> ApprovalDecision:
        decision = self._evaluator.evaluate(action)
        self._audit(action, decision)
        return decision

    def evaluate_command(self, command: ProposedCommand) -> ApprovalDecision:
        decision = self._evaluator.evaluate_command(command)
        self._audit(command, decision)
        return decision

    def _audit(self, action: ProposedAction, decision: ApprovalDecision) -> None:
        write_audit(
            event="agent_tool_approval_run",
            payload={
                "agent_name": self.agent_name,
                "project": action.project_name,
                "action_type": action.action_type,
                "source_agent": action.source_agent,
                "status": decision.status,
                "risk_level": decision.risk_level,
            },
            logs_root=get_logs_dir(),
            stream="tool-calls",
        )

    def _format_decision(self, decision: ApprovalDecision) -> str:
        lines = [
            f"Status: {decision.status}",
            f"Risk: {decision.risk_level}",
            f"Reason: {decision.reason}",
            "",
            "Findings:",
        ]
        lines.extend(f"- [{item.severity}] {item.category}: {item.detail}" for item in decision.findings)
        if decision.requirements:
            lines.extend(["", "Requirements:"])
            lines.extend(f"- {item.requirement_type}: {item.detail}" for item in decision.requirements)
        if decision.preview:
            lines.extend(["", "Preview:"])
            lines.append(f"- {decision.preview.summary}")
            if decision.preview.command_preview:
                lines.append(f"- command: {decision.preview.command_preview}")
            if decision.preview.working_directory:
                lines.append(f"- working_directory: {decision.preview.working_directory}")
        lines.extend(["", f"Next step: {decision.suggested_next_step}"])
        lines.append("No command is executed in this flow.")
        return "\n".join(lines)
