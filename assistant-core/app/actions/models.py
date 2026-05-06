"""Dataclass contracts for ATLAS intent/action planning.

These models intentionally contain no execution or adapter code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.actions.risk import DEFAULT_ACTION_RISK, RiskLevel, requires_confirmation
from app.actions.types import ActionSource, ActionStatus, ActionType, IntentCategory, PermissionStatus


@dataclass(slots=True)
class IntentResult:
    intent_id: str
    category: IntentCategory
    confidence: float
    language: str
    raw_text: str
    normalized_text: str
    entities: dict[str, Any] = field(default_factory=dict)
    target: str = ""
    action_candidate: ActionType | None = None
    ambiguity_reason: str = ""
    requires_clarification: bool = False
    safety_notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.category is IntentCategory.AMBIGUOUS:
            self.requires_clarification = True
            if not self.ambiguity_reason:
                self.ambiguity_reason = "Intent target or action is ambiguous."
        if self.category in {IntentCategory.UNKNOWN, IntentCategory.BLOCKED}:
            self.action_candidate = None


@dataclass(slots=True)
class ActionCandidate:
    action_id: str
    action_type: ActionType
    target: str
    parameters: dict[str, Any]
    source: ActionSource
    user_goal: str
    intent_category: IntentCategory
    risk_level: RiskLevel
    requires_confirmation: bool
    dry_run_supported: bool
    reversible: bool
    expected_result: str
    blocked_reason: str = ""
    confirmation_prompt: str = ""
    audit_metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        default_risk = DEFAULT_ACTION_RISK.get(self.action_type)
        if default_risk is RiskLevel.BLOCKED:
            self.risk_level = RiskLevel.BLOCKED
        if self.risk_level is RiskLevel.BLOCKED:
            self.requires_confirmation = False
            self.reversible = False
            if not self.blocked_reason:
                raise ValueError("blocked actions require blocked_reason")
        if requires_confirmation(self.risk_level, source=self.source) and not self.requires_confirmation:
            raise ValueError("medium/high actions require confirmation")
        if self.source is ActionSource.VOICE and self.risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH}:
            self.requires_confirmation = True


@dataclass(slots=True)
class ActionPreview:
    action_id: str
    summary: str
    target: str
    parameters_preview: dict[str, Any]
    risk_level: RiskLevel
    will_change_state: bool
    requires_confirmation: bool
    reversible: bool
    estimated_effect: str
    warnings: list[str] = field(default_factory=list)
    safe_to_execute: bool = False
    blocked_reason: str = ""
    requires_clarification: bool = False

    def __post_init__(self) -> None:
        if self.requires_clarification:
            self.safe_to_execute = False
            self.requires_confirmation = False
            return
        if self.risk_level is RiskLevel.BLOCKED:
            self.safe_to_execute = False
            self.requires_confirmation = False
            if not self.blocked_reason:
                raise ValueError("blocked previews require blocked_reason")
        if self.risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH} and not self.requires_confirmation:
            raise ValueError("medium/high previews require confirmation")


@dataclass(slots=True)
class ActionResult:
    action_id: str
    status: ActionStatus
    executed: bool
    dry_run: bool
    message: str
    result_data: dict[str, Any] = field(default_factory=dict)
    error_code: str = ""
    error_message: str = ""
    audit_metadata: dict[str, Any] = field(default_factory=dict)
    started_at: datetime | None = None
    finished_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.dry_run and self.executed:
            raise ValueError("dry-run results cannot be executed")
        if self.status is not ActionStatus.EXECUTED and self.executed:
            raise ValueError("executed=True is only valid for executed status")
        if self.status in {
            ActionStatus.PLANNED,
            ActionStatus.PREVIEWED,
            ActionStatus.AWAITING_CONFIRMATION,
            ActionStatus.DENIED,
            ActionStatus.BLOCKED,
            ActionStatus.CANCELLED,
            ActionStatus.SKIPPED,
        }:
            self.executed = False


@dataclass(slots=True)
class PermissionDecision:
    action_id: str
    status: PermissionStatus
    risk_level: RiskLevel
    allowed_to_execute: bool
    requires_confirmation: bool
    requires_clarification: bool
    blocked: bool
    reason: str
    confirmation_prompt: str
    warnings: list[str]
    audit_metadata: dict[str, Any]
    next_step: str
    preview: ActionPreview | None = None

    def __post_init__(self) -> None:
        if self.status is PermissionStatus.BLOCKED:
            self.blocked = True
            self.allowed_to_execute = False
            self.requires_confirmation = False
        if self.status is PermissionStatus.CLARIFICATION_REQUIRED:
            self.requires_clarification = True
            self.allowed_to_execute = False
            self.requires_confirmation = False
        if self.status is PermissionStatus.CONFIRMATION_REQUIRED:
            self.requires_confirmation = True
            self.allowed_to_execute = False
        if self.status in {PermissionStatus.DENIED, PermissionStatus.CANCELLED, PermissionStatus.UNKNOWN}:
            self.allowed_to_execute = False
        if self.blocked:
            self.allowed_to_execute = False


@dataclass(slots=True)
class ClarificationRequest:
    reason: str
    missing_fields: list[str]
    candidate_targets: list[str]
    suggested_questions: list[str]
    safe_default: str = "no_action"

    def __post_init__(self) -> None:
        if self.safe_default != "no_action":
            raise ValueError("clarification safe_default must be no_action")
