from datetime import timedelta

from app.actions.types import ActionSource
from app.execution.gate import SafeExecutionGate
from app.execution.models import ExecutionMode, ExecutionRequest, ExecutionStatus
from app.execution.service import ExecutionService
from app.panel.policy import utcnow
from app.panel.service import PermissionPanelService
from app.panel.store import InMemoryPanelStore


def test_chrome_open_is_eligible_but_not_executable() -> None:
    service = ExecutionService(panel_store=InMemoryPanelStore())
    plan = service.from_text("Chrome'u ac", mode=ExecutionMode.PREVIEW_ONLY)
    assert plan.eligible is True
    assert plan.executable is False


def test_unknown_target_is_not_eligible() -> None:
    gate = SafeExecutionGate()
    request = ExecutionRequest(
        request_id="req-1",
        source="text",
        requested_mode=ExecutionMode.PREVIEW_ONLY,
        metadata={"action_type": "pc.open_app", "target": "Opera", "risk_level": "low", "permission_status": "preview_allowed"},
    )
    eligibility = gate.evaluate(request)
    assert eligibility.eligible is False


def test_secret_read_is_blocked() -> None:
    service = ExecutionService(panel_store=InMemoryPanelStore())
    plan = service.from_text("Sifrelerimi oku", mode=ExecutionMode.PREVIEW_ONLY)
    assert plan.eligible is False
    assert "blocked" in plan.blocked_reason.lower()


def test_home_action_not_pc_eligible() -> None:
    service = ExecutionService(panel_store=InMemoryPanelStore())
    plan = service.from_text("Salon isigini ac", mode=ExecutionMode.PREVIEW_ONLY)
    assert plan.eligible is False
    assert "blocked" in plan.blocked_reason.lower() or "home/device" in plan.blocked_reason.lower()


def test_approved_panel_item_is_armed_for_future() -> None:
    store = InMemoryPanelStore()
    panel = PermissionPanelService(store=store)
    created = panel.submit_text("Chrome'u ac", source=ActionSource.TEXT)
    panel.approve_item(created.item.item_id)
    service = ExecutionService(panel_store=store)
    plan = service.from_panel_item(created.item.item_id, mode=ExecutionMode.PREVIEW_ONLY)
    result = service.execute_plan(plan)
    assert result.status is ExecutionStatus.ARMED_FOR_FUTURE
    assert result.executed is False


def test_expired_panel_item_is_denied_or_expired() -> None:
    store = InMemoryPanelStore()
    panel = PermissionPanelService(store=store)
    created = panel.submit_text("Chrome'u ac", source=ActionSource.TEXT)
    created.item.expires_at = utcnow() - timedelta(seconds=5)
    store.update(created.item)
    service = ExecutionService(panel_store=store)
    plan = service.from_panel_item(created.item.item_id, mode=ExecutionMode.PREVIEW_ONLY)
    result = service.execute_plan(plan)
    assert result.status is ExecutionStatus.EXPIRED


def test_blocked_panel_item_stays_blocked() -> None:
    store = InMemoryPanelStore()
    panel = PermissionPanelService(store=store)
    created = panel.submit_text("Sifrelerimi oku", source=ActionSource.TEXT)
    service = ExecutionService(panel_store=store)
    plan = service.from_panel_item(created.item.item_id, mode=ExecutionMode.PREVIEW_ONLY)
    result = service.execute_plan(plan)
    assert result.status is ExecutionStatus.BLOCKED


def test_execute_mode_still_does_not_execute() -> None:
    store = InMemoryPanelStore()
    panel = PermissionPanelService(store=store)
    created = panel.submit_text("Chrome'u ac", source=ActionSource.TEXT)
    panel.approve_item(created.item.item_id)
    service = ExecutionService(panel_store=store)
    plan = service.from_panel_item(created.item.item_id, mode=ExecutionMode.EXECUTED)
    result = service.execute_plan(plan)
    assert result.executed is False
    assert result.audit_metadata["real_execution_attempted"] is False
    assert result.audit_metadata["shell_used"] is False
