"""Audit metadata helpers for personal action permission decisions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.actions.models import ActionCandidate
from app.actions.risk import RiskLevel
from app.actions.types import PermissionStatus

POLICY_VERSION = "action-permission-v1"


def build_permission_audit_metadata(
    action: ActionCandidate,
    *,
    decision_status: PermissionStatus,
    requires_confirmation: bool,
    blocked: bool,
    policy_version: str = POLICY_VERSION,
) -> dict[str, Any]:
    """Build audit metadata without attempting execution."""

    metadata: dict[str, Any] = {
        "action_id": action.action_id,
        "action_type": action.action_type.value,
        "intent_category": action.intent_category.value,
        "risk_level": action.risk_level.value,
        "source": action.source.value,
        "decision_status": decision_status.value,
        "requires_confirmation": requires_confirmation,
        "blocked": blocked,
        "target_summary": _summarize_target(action.target),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "policy_version": policy_version,
        "execution_attempted": False,
    }
    if "confidence" in action.audit_metadata:
        metadata["confidence"] = action.audit_metadata["confidence"]
    if "intent_id" in action.audit_metadata:
        metadata["intent_id"] = action.audit_metadata["intent_id"]
    return metadata


def result_audit_metadata(decision_metadata: dict[str, Any], *, result_status: str) -> dict[str, Any]:
    """Copy decision audit metadata into a non-executing ActionResult record."""

    metadata = dict(decision_metadata)
    metadata["result_status"] = result_status
    metadata["execution_attempted"] = False
    return metadata


def _summarize_target(target: str) -> str:
    value = target.strip() or "<missing>"
    if len(value) <= 120:
        return value
    return f"{value[:117]}..."
