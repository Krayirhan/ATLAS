from __future__ import annotations

from app.actions import ActionSource, ActionType, IntentCategory, RiskLevel
from app.actions.models import ActionCandidate
from app.devices import (
    DeviceActionPlanner,
    DeviceCapability,
    DeviceCapabilityType,
    DeviceDefinition,
    DeviceRegistry,
    DeviceType,
    RoomDefinition,
)


def test_device_models_construct() -> None:
    room = RoomDefinition(room_id="salon", display_name="Salon")
    capability = DeviceCapability(
        capability=DeviceCapabilityType.POWER,
        supported=True,
        readable=False,
        writable=True,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
    )
    device = DeviceDefinition(
        device_id="salon-isigi",
        display_name="Salon Isigi",
        device_type=DeviceType.LIGHT,
        room_id=room.room_id,
        capabilities=[capability],
    )
    assert room.display_name == "Salon"
    assert device.display_name == "Salon Isigi"


def test_registry_lists_builtin_rooms_and_devices() -> None:
    registry = DeviceRegistry()
    assert len(registry.list_rooms()) >= 5
    assert len(registry.list_devices()) >= 5
    assert registry.get_device("salon-isigi") is not None


def test_registry_alias_finds_salon_light() -> None:
    registry = DeviceRegistry()
    device = registry.find_device_by_alias("ana isik")
    assert device is not None
    assert device.device_id == "salon-isigi"


def test_registry_room_alias_works() -> None:
    registry = DeviceRegistry()
    room = registry.find_room_by_alias("ofis")
    assert room is not None
    assert room.room_id == "calisma-odasi"


def test_planner_device_turn_on_requires_confirmation() -> None:
    planner = DeviceActionPlanner()
    result = planner.preview_device_action("Salon isigini ac")
    assert result.plan is not None
    assert result.plan.requires_confirmation is True
    assert result.plan.risk_level is RiskLevel.MEDIUM


def test_planner_state_query_is_safe_readonly() -> None:
    planner = DeviceActionPlanner()
    action = ActionCandidate(
        action_id="a2",
        action_type=ActionType.DEVICE_STATE_QUERY,
        target="salon isik",
        parameters={"room_name": "salon", "device_name": "isik"},
        source=ActionSource.TEXT,
        user_goal="Salon isigimin durumu ne",
        intent_category=IntentCategory.DEVICE_STATE_QUERY,
        risk_level=RiskLevel.SAFE_READONLY,
        requires_confirmation=False,
        dry_run_supported=True,
        reversible=True,
        expected_result="state preview",
    )
    plan = planner.build_plan(action)
    assert plan.risk_level is RiskLevel.SAFE_READONLY
    assert plan.requires_confirmation is False


def test_planner_unsupported_capability_is_blocked() -> None:
    planner = DeviceActionPlanner()
    action = ActionCandidate(
        action_id="a3",
        action_type=ActionType.DEVICE_SET_TEMPERATURE,
        target="salon isik",
        parameters={"room_name": "salon", "device_name": "isik", "temperature": 24},
        source=ActionSource.TEXT,
        user_goal="Salon isigini 24 derece yap",
        intent_category=IntentCategory.DEVICE_SET_TEMPERATURE,
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        dry_run_supported=True,
        reversible=True,
        expected_result="blocked",
    )
    plan = planner.build_plan(action)
    assert plan.blocked is True
    assert plan.safe_to_execute is False
    assert plan.audit_metadata["execution_attempted"] is False
