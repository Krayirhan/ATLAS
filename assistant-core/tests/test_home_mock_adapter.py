from __future__ import annotations

from app.actions import ActionSource, ActionType, IntentCategory, RiskLevel
from app.actions.models import ActionCandidate
from app.devices import DeviceActionPlanner
from app.home.mock_adapter import MockHomeControlAdapter
from app.home.models import HomeStateReadRequest, HomeStateWriteRequest


def test_home_models_construct() -> None:
    from app.home.models import HomeAdapterCapability, HomeControlPlan, HomeControlResult, HomeControlStatus, HomeStateReadResult

    capability = HomeAdapterCapability("mock", "power", False, True, False, True, RiskLevel.MEDIUM)
    plan = HomeControlPlan(
        plan_id="home-1",
        device_id="salon-isigi",
        room_id="salon",
        action_type="device.turn_on",
        capability="power",
        parameters={},
        risk_level=RiskLevel.MEDIUM,
        requires_confirmation=True,
        state_read=False,
        state_write=True,
        adapter_name="mock",
        supported=True,
        dry_run=True,
        executable=False,
        execution_allowed=False,
        safe_to_preview=True,
        safe_to_execute=False,
        blocked=False,
        blocked_reason="",
    )
    result = HomeControlResult(plan_id="home-1", status=HomeControlStatus.PREVIEWED, executed=False, dry_run=True, message="ok")
    read_result = HomeStateReadResult("salon-isigi", "state_query", True, "off", False, "mock", "ok")
    assert capability.capability == "power"
    assert plan.device_id == "salon-isigi"
    assert result.executed is False
    assert read_result.supported is True


def test_mock_adapter_health_check_ok() -> None:
    adapter = MockHomeControlAdapter()
    status = adapter.health_check()
    assert status["ok"] is True
    assert status["network_used"] is False
    assert status["physical_device_touched"] is False


def test_mock_adapter_read_state() -> None:
    adapter = MockHomeControlAdapter()
    result = adapter.read_state(HomeStateReadRequest(device_id="salon-isigi", capability="power"))
    assert result.supported is True
    assert result.metadata["network_used"] is False
    assert result.metadata["physical_device_touched"] is False
    assert result.metadata["execution_attempted"] is False


def test_mock_adapter_write_state_does_not_execute() -> None:
    adapter = MockHomeControlAdapter()
    result = adapter.write_state(HomeStateWriteRequest(device_id="salon-isigi", capability="power", value="on", requires_confirmation=True))
    assert result.executed is False
    assert result.dry_run is True
    assert result.metadata["network_used"] is False
    assert result.metadata["physical_device_touched"] is False
    assert result.metadata["execution_attempted"] is False


def test_mock_adapter_execute_does_not_touch_device() -> None:
    planner = DeviceActionPlanner()
    device_plan = planner.preview_device_action("Salon isigini ac").plan
    assert device_plan is not None
    adapter = MockHomeControlAdapter()
    home_plan = adapter.build_plan(device_plan)
    result = adapter.execute(home_plan)
    assert result.executed is False
    assert result.audit_metadata["network_used"] is False
    assert result.audit_metadata["physical_device_touched"] is False
    assert result.audit_metadata["execution_attempted"] is False
