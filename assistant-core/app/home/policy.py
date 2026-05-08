from __future__ import annotations

from app.actions.risk import RiskLevel
from app.devices.models import DeviceActionPlan


def is_state_read(action_type: str, capability: str) -> bool:
    return action_type == "device.state_query" or capability == "state_query"


def is_state_write(action_type: str, capability: str) -> bool:
    return not is_state_read(action_type, capability)


def capability_supported(plan: DeviceActionPlan) -> bool:
    if plan.blocked or plan.clarification_required:
        return False
    if not plan.supported:
        return False
    if plan.capability in {"camera_stream", "lock"}:
        return False
    return True


def home_risk_for_plan(plan: DeviceActionPlan) -> RiskLevel:
    if plan.blocked:
        return RiskLevel.BLOCKED
    if plan.capability in {"camera_stream", "lock"}:
        return RiskLevel.BLOCKED
    if plan.action_type in {"device.open_door", "device.unlock", "device.disable_security"}:
        return RiskLevel.BLOCKED
    if is_state_read(plan.action_type, plan.capability):
        return RiskLevel.SAFE_READONLY
    return plan.risk_level


def blocked_reason_for_plan(plan: DeviceActionPlan) -> str:
    if plan.blocked_reason:
        return plan.blocked_reason
    if plan.capability == "camera_stream":
        return "Kamera stream capability privacy riski nedeniyle blocked."
    if plan.capability == "lock":
        return "Kilit veya kapi capability fiziksel guvenlik nedeniyle blocked."
    return "Home control action MVP policy tarafindan unsupported."


def base_audit_metadata(plan: DeviceActionPlan, adapter_name: str) -> dict[str, object]:
    return {
        "device_action_id": plan.action_id,
        "device_id": plan.target_device_id,
        "room_id": plan.target_room_id,
        "action_type": plan.action_type,
        "capability": plan.capability,
        "adapter_name": adapter_name,
        "execution_attempted": False,
        "network_used": False,
        "physical_device_touched": False,
    }
