from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PanelItemType(str, Enum):
    ACTION_PREVIEW = "action_preview"
    CONFIRMATION_REQUIRED = "confirmation_required"
    CLARIFICATION_REQUIRED = "clarification_required"
    BLOCKED = "blocked"
    DENIED = "denied"
    APPROVED_PREVIEW = "approved_preview"
    CANCELLED = "cancelled"
    INFO = "info"


class PanelItemStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    EXPIRED = "expired"
    RESOLVED = "resolved"


class PanelDecisionType(str, Enum):
    APPROVE = "approve"
    DENY = "deny"
    CANCEL = "cancel"
    ACKNOWLEDGE = "acknowledge"


class PanelDecision(BaseModel):
    decision_id: str
    item_id: str
    decision: PanelDecisionType
    reason: str = ""
    decided_at: datetime = Field(default_factory=_utcnow)
    user_confirmed: bool = False
    execution_allowed: bool = False
    execution_attempted: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class PermissionPanelItem(BaseModel):
    item_id: str
    item_type: PanelItemType
    status: PanelItemStatus
    title: str
    summary: str
    user_message: str
    action_type: str = ""
    target: str = ""
    risk_level: str = ""
    source: str = "text"
    requires_confirmation: bool = False
    confirmation_prompt: str = ""
    warnings: list[str] = Field(default_factory=list)
    blocked_reason: str = ""
    clarification_prompt: str = ""
    preview_payload: dict[str, Any] = Field(default_factory=dict)
    permission_decision: dict[str, Any] | None = None
    pc_plan: dict[str, Any] | None = None
    home_plan: dict[str, Any] | None = None
    routine_preview: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=_utcnow)
    expires_at: datetime | None = None
    audit_metadata: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    last_decision: PanelDecision | None = None


class PermissionPanelState(BaseModel):
    pending_count: int
    blocked_count: int
    approved_count: int
    denied_count: int
    cancelled_count: int
    items: list[PermissionPanelItem] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PanelOperationStatus(str, Enum):
    CREATED = "created"
    LISTED = "listed"
    SHOWN = "shown"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    NOT_FOUND = "not_found"
    INVALID = "invalid"
    SKIPPED = "skipped"


class PanelOperationResult(BaseModel):
    status: PanelOperationStatus
    message: str
    item: PermissionPanelItem | None = None
    items: list[PermissionPanelItem] = Field(default_factory=list)
    decision: PanelDecision | None = None
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
