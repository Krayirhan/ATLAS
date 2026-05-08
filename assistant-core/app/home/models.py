from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.actions.risk import RiskLevel
from app.actions.types import ActionSource
from app.devices.models import DeviceActionPlan


class HomeControlStatus(str, Enum):
    PREVIEWED = "previewed"
    STATE_READ = "state_read"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    BLOCKED = "blocked"
    UNSUPPORTED = "unsupported"
    SKIPPED = "skipped"
    FAILED = "failed"
    EXECUTED = "executed"


@dataclass(slots=True)
class HomeControlRequest:
    project_name: str
    device_action_plan: DeviceActionPlan
    source: ActionSource
    dry_run: bool
    execute: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class HomeControlPlan:
    plan_id: str
    device_id: str
    room_id: str
    action_type: str
    capability: str
    parameters: dict[str, Any]
    risk_level: RiskLevel
    requires_confirmation: bool
    state_read: bool
    state_write: bool
    adapter_name: str
    supported: bool
    dry_run: bool
    executable: bool
    execution_allowed: bool
    safe_to_preview: bool
    safe_to_execute: bool
    blocked: bool
    blocked_reason: str
    warnings: list[str] = field(default_factory=list)
    summary: str = ""
    audit_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class HomeControlResult:
    plan_id: str
    status: HomeControlStatus
    executed: bool
    dry_run: bool
    message: str
    state_before: dict[str, Any] = field(default_factory=dict)
    state_after: dict[str, Any] = field(default_factory=dict)
    data: dict[str, Any] = field(default_factory=dict)
    error_code: str = ""
    error_message: str = ""
    audit_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class HomeStateReadRequest:
    device_id: str
    capability: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class HomeStateReadResult:
    device_id: str
    capability: str
    supported: bool
    value: Any
    stale: bool
    source: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class HomeStateWriteRequest:
    device_id: str
    capability: str
    value: Any
    requires_confirmation: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class HomeStateWriteResult:
    device_id: str
    capability: str
    accepted: bool
    executed: bool
    dry_run: bool
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class HomeAdapterCapability:
    adapter_name: str
    capability: str
    state_read_supported: bool
    state_write_supported: bool
    execution_supported: bool
    dry_run_supported: bool
    risk_level: RiskLevel
    notes: list[str] = field(default_factory=list)
