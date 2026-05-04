"""Dataclasses for preview-only tool approval decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ActionType = Literal[
    "command",
    "file_change",
    "tool_call",
    "git_operation",
    "mcp_operation",
    "documentation_write",
    "test_write",
    "unknown",
]
ApprovalStatus = Literal["blocked", "approval_required", "preview_allowed", "safe_readonly", "unknown"]
ApprovalSeverity = Literal["critical", "high", "medium", "low", "info"]


@dataclass(slots=True)
class ProposedAction:
    action_type: ActionType = "unknown"
    project_name: str = ""
    reason: str = ""
    source_agent: str = ""
    user_goal: str = ""


@dataclass(slots=True)
class ProposedCommand(ProposedAction):
    command: str = ""
    working_directory: str = ""
    action_type: ActionType = "command"


@dataclass(slots=True)
class ProposedFileChange(ProposedAction):
    file_path: str = ""
    change_type: ActionType = "file_change"
    action_type: ActionType = "file_change"


@dataclass(slots=True)
class ProposedToolCall(ProposedAction):
    tool_name: str = ""
    arguments_summary: str = ""
    action_type: ActionType = "tool_call"


@dataclass(slots=True)
class ApprovalRisk:
    severity: ApprovalSeverity
    title: str
    detail: str


@dataclass(slots=True)
class ApprovalFinding:
    severity: ApprovalSeverity
    category: str
    detail: str


@dataclass(slots=True)
class ApprovalPreview:
    summary: str
    command_preview: str = ""
    working_directory: str = ""


@dataclass(slots=True)
class ApprovalRequirement:
    requirement_type: str
    detail: str


@dataclass(slots=True)
class ApprovalDecision:
    status: ApprovalStatus
    risk_level: ApprovalSeverity
    reason: str
    findings: list[ApprovalFinding]
    approval_required: bool
    blocked: bool
    safe_preview: bool
    suggested_next_step: str
    audit_metadata: dict[str, Any] = field(default_factory=dict)
    preview: ApprovalPreview | None = None
    requirements: list[ApprovalRequirement] = field(default_factory=list)
