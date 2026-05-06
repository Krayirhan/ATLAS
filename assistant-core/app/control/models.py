from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.actions.models import PermissionDecision
from app.actions.types import ActionSource
from app.actions.risk import RiskLevel

class PCControlStatus(str, Enum):
    PLANNED = "planned"
    PREVIEWED = "previewed"
    READY = "ready"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"
    EXECUTED = "executed"

@dataclass(slots=True)
class PCControlRequest:
    action: Any  # ActionCandidate
    permission_decision: PermissionDecision
    dry_run: bool
    execute: bool
    user_goal: str
    source: ActionSource
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class PCControlPlan:
    action_id: str
    action_type: str
    target: str
    resolved_target: str
    capability: Any  # PCActionCapability
    dry_run: bool
    executable: bool
    execution_allowed: bool
    risk_level: RiskLevel
    requires_confirmation: bool
    summary: str
    warnings: list[str] = field(default_factory=list)
    blocked_reason: str = ""
    audit_metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class PCControlResult:
    action_id: str
    status: PCControlStatus
    executed: bool
    dry_run: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    error_code: str = ""
    error_message: str = ""
    audit_metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class PCActionCapability:
    action_type: str
    supported: bool
    execution_supported: bool
    dry_run_supported: bool
    requires_allowlist: bool
    risk_level: RiskLevel
    description: str
    limitations: list[str] = field(default_factory=list)
