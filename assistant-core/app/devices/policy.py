from __future__ import annotations

from app.actions.models import ActionCandidate
from app.actions.risk import RiskLevel
from app.actions.types import ActionType
from app.devices.models import DeviceActionPlan, DeviceTargetResolution


def device_audit_metadata(action: ActionCandidate, resolution: DeviceTargetResolution) -> dict[str, object]:
    return {
        "action_id": action.action_id,
        "action_type": action.action_type.value,
        "target": action.target,
        "resolved_device_id": resolution.device.device_id if resolution.device else "",
        "resolved_room_id": resolution.room.room_id if resolution.room else "",
        "resolution_confidence": resolution.confidence,
        "requires_clarification": resolution.requires_clarification,
        "execution_attempted": False,
        "planner": "device-action-planner-mvp",
    }


def plan_from_resolution(
    *,
    action: ActionCandidate,
    resolution: DeviceTargetResolution,
    capability: str = "",
    risk_level: RiskLevel,
    requires_confirmation: bool,
    supported: bool,
    blocked: bool,
    blocked_reason: str = "",
    clarification_required: bool = False,
    warnings: list[str] | None = None,
    summary: str = "",
) -> DeviceActionPlan:
    return DeviceActionPlan(
        action_id=action.action_id,
        action_type=action.action_type.value,
        target_device_id=resolution.device.device_id if resolution.device else "",
        target_room_id=resolution.room.room_id if resolution.room else "",
        capability=capability,
        parameters=dict(action.parameters),
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        supported=supported,
        safe_to_preview=True,
        safe_to_execute=False,
        blocked=blocked,
        blocked_reason=blocked_reason,
        clarification_required=clarification_required,
        summary=summary,
        warnings=warnings or [],
        audit_metadata=device_audit_metadata(action, resolution),
    )


def should_block_text(text: str) -> bool:
    normalized = text.lower()
    return "kamera" in normalized or "kapi" in normalized


def text_block_reason(text: str) -> str:
    normalized = text.lower()
    if "kamera" in normalized:
        return "Kamera aksiyonlari privacy riski nedeniyle MVP'de blocked."
    if "kapi" in normalized:
        return "Kapi/lock aksiyonlari fiziksel guvenlik nedeniyle MVP'de blocked."
    return "Bu cihaz aksiyonu MVP policy tarafindan blocked."
