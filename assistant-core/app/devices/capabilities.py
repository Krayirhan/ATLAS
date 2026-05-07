from __future__ import annotations

from dataclasses import dataclass, field

from app.actions.risk import RiskLevel
from app.actions.types import ActionType
from app.devices.models import DeviceCapability, DeviceCapabilityType, DeviceDefinition


@dataclass(slots=True)
class DeviceCapabilityRule:
    action_type: ActionType
    required_capability: DeviceCapabilityType
    risk_level: RiskLevel
    requires_confirmation: bool
    blocked: bool = False
    unsupported_reason: str = ""
    warnings: list[str] = field(default_factory=list)


CAPABILITY_RULES: dict[ActionType, DeviceCapabilityRule] = {
    ActionType.DEVICE_TURN_ON: DeviceCapabilityRule(
        action_type=ActionType.DEVICE_TURN_ON,
        required_capability=DeviceCapabilityType.POWER,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
    ),
    ActionType.DEVICE_TURN_OFF: DeviceCapabilityRule(
        action_type=ActionType.DEVICE_TURN_OFF,
        required_capability=DeviceCapabilityType.POWER,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
    ),
    ActionType.DEVICE_SET_BRIGHTNESS: DeviceCapabilityRule(
        action_type=ActionType.DEVICE_SET_BRIGHTNESS,
        required_capability=DeviceCapabilityType.BRIGHTNESS,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
    ),
    ActionType.DEVICE_SET_TEMPERATURE: DeviceCapabilityRule(
        action_type=ActionType.DEVICE_SET_TEMPERATURE,
        required_capability=DeviceCapabilityType.TEMPERATURE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
    ),
    ActionType.DEVICE_STATE_QUERY: DeviceCapabilityRule(
        action_type=ActionType.DEVICE_STATE_QUERY,
        required_capability=DeviceCapabilityType.STATE_QUERY,
        risk_level=RiskLevel.SAFE_READONLY,
        requires_confirmation=False,
    ),
    ActionType.DEVICE_UNLOCK: DeviceCapabilityRule(
        action_type=ActionType.DEVICE_UNLOCK,
        required_capability=DeviceCapabilityType.LOCK,
        risk_level=RiskLevel.BLOCKED,
        requires_confirmation=False,
        blocked=True,
        unsupported_reason="Kilit acma aksiyonlari MVP'de blocked.",
    ),
    ActionType.DEVICE_OPEN_DOOR: DeviceCapabilityRule(
        action_type=ActionType.DEVICE_OPEN_DOOR,
        required_capability=DeviceCapabilityType.LOCK,
        risk_level=RiskLevel.BLOCKED,
        requires_confirmation=False,
        blocked=True,
        unsupported_reason="Kapi acma aksiyonlari MVP'de blocked.",
    ),
    ActionType.DEVICE_DISABLE_SECURITY: DeviceCapabilityRule(
        action_type=ActionType.DEVICE_DISABLE_SECURITY,
        required_capability=DeviceCapabilityType.CAMERA_STREAM,
        risk_level=RiskLevel.BLOCKED,
        requires_confirmation=False,
        blocked=True,
        unsupported_reason="Privacy-sensitive kamera/security aksiyonlari MVP'de blocked.",
    ),
}


def get_capability_rule(action_type: ActionType) -> DeviceCapabilityRule | None:
    return CAPABILITY_RULES.get(action_type)


def device_supports(device: DeviceDefinition, capability_type: DeviceCapabilityType) -> DeviceCapability | None:
    for capability in device.capabilities:
        if capability.capability is capability_type and capability.supported:
            return capability
    return None
