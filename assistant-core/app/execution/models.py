from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ExecutionMode(str, Enum):
    DISABLED = "disabled"
    DRY_RUN = "dry_run"
    PREVIEW_ONLY = "preview_only"
    ARMED_FOR_FUTURE = "armed_for_future"
    EXECUTED = "executed"


class ExecutionStatus(str, Enum):
    PREVIEWED = "previewed"
    ELIGIBLE = "eligible"
    BLOCKED = "blocked"
    DENIED = "denied"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    ARMED_FOR_FUTURE = "armed_for_future"
    SKIPPED = "skipped"
    FAILED = "failed"
    EXECUTED = "executed"


class RollbackPlan(BaseModel):
    available: bool = False
    description: str = ""
    steps: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionRequest(BaseModel):
    request_id: str
    source: str
    action_candidate: Any | None = None
    permission_decision: Any | None = None
    pc_plan: Any | None = None
    home_plan: Any | None = None
    panel_item: Any | None = None
    requested_mode: ExecutionMode = ExecutionMode.PREVIEW_ONLY
    user_confirmed: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionEligibility(BaseModel):
    eligible: bool
    allowed_by_policy: bool
    allowed_by_allowlist: bool
    requires_panel_approval: bool
    has_panel_approval: bool
    risk_level: str
    action_type: str
    target: str
    reason: str
    warnings: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionPlan(BaseModel):
    execution_id: str
    action_type: str
    target: str
    resolved_target: str
    mode: ExecutionMode
    eligible: bool
    executable: bool
    will_execute: bool
    dry_run: bool
    requires_approval: bool
    approved: bool
    rollback_available: bool
    rollback_plan: RollbackPlan = Field(default_factory=RollbackPlan)
    warnings: list[str] = Field(default_factory=list)
    blocked_reason: str = ""
    audit_metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    execution_id: str
    status: ExecutionStatus
    executed: bool
    dry_run: bool
    message: str
    error_code: str = ""
    error_message: str = ""
    audit_metadata: dict[str, Any] = Field(default_factory=dict)

