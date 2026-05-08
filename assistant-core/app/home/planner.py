from __future__ import annotations

from uuid import uuid4

from app.actions.risk import RiskLevel
from app.actions.types import ActionSource
from app.devices.planner import DeviceActionPlanner
from app.devices.models import DeviceActionPlan, DeviceRegistryStatus
from app.home.models import HomeControlPlan, HomeControlResult, HomeControlStatus
from app.home.policy import (
    base_audit_metadata,
    blocked_reason_for_plan,
    capability_supported,
    home_risk_for_plan,
    is_state_read,
    is_state_write,
)


class HomeControlPlanner:
    def __init__(self, *, adapter_name: str = "mock_home_control", device_planner: DeviceActionPlanner | None = None) -> None:
        self.adapter_name = adapter_name
        self.device_planner = device_planner or DeviceActionPlanner()

    def build_plan(self, device_action_plan: DeviceActionPlan) -> HomeControlPlan:
        risk_level = home_risk_for_plan(device_action_plan)
        state_read = is_state_read(device_action_plan.action_type, device_action_plan.capability)
        state_write = is_state_write(device_action_plan.action_type, device_action_plan.capability)
        supported = capability_supported(device_action_plan)
        blocked = device_action_plan.blocked or risk_level is RiskLevel.BLOCKED
        requires_clarification = device_action_plan.clarification_required
        blocked_reason = blocked_reason_for_plan(device_action_plan) if blocked or not supported else ""
        requires_confirmation = False if state_read else device_action_plan.requires_confirmation
        summary = device_action_plan.summary or "Home preview plan hazir."
        if state_read:
            summary = f"{device_action_plan.target_device_id} icin state-read preview hazir. Gercek ag veya cihaz erisimi yok."
        elif blocked:
            summary = blocked_reason
        elif state_write:
            summary = (
                f"{device_action_plan.target_device_id} icin {device_action_plan.action_type} home preview hazir. "
                "Gercek home execution yok."
            )

        audit_metadata = base_audit_metadata(device_action_plan, self.adapter_name)
        audit_metadata.update(device_action_plan.audit_metadata)
        audit_metadata["requires_clarification"] = requires_clarification
        return HomeControlPlan(
            plan_id=f"home-{uuid4().hex[:12]}",
            device_id=device_action_plan.target_device_id,
            room_id=device_action_plan.target_room_id,
            action_type=device_action_plan.action_type,
            capability=device_action_plan.capability,
            parameters=dict(device_action_plan.parameters),
            risk_level=risk_level,
            requires_confirmation=requires_confirmation,
            state_read=state_read,
            state_write=state_write,
            adapter_name=self.adapter_name,
            supported=supported,
            dry_run=True,
            executable=False,
            execution_allowed=False,
            safe_to_preview=True,
            safe_to_execute=False,
            blocked=blocked,
            blocked_reason=blocked_reason,
            warnings=list(device_action_plan.warnings),
            summary=summary,
            audit_metadata=audit_metadata,
        )

    def preview_from_text(self, text: str, source: ActionSource = ActionSource.TEXT) -> HomeControlResult:
        device_result = self.device_planner.preview_device_action(text, source=source)
        if device_result.plan is None:
            status = HomeControlStatus.BLOCKED if device_result.status is DeviceRegistryStatus.BLOCKED else HomeControlStatus.UNSUPPORTED
            if device_result.status is DeviceRegistryStatus.AMBIGUOUS:
                status = HomeControlStatus.UNSUPPORTED
            return HomeControlResult(
                plan_id="",
                status=status,
                executed=False,
                dry_run=True,
                message=device_result.message,
                audit_metadata={
                    "execution_attempted": False,
                    "network_used": False,
                    "physical_device_touched": False,
                    "device_status": device_result.status.value,
                },
            )
        plan = self.build_plan(device_result.plan)
        if plan.audit_metadata.get("requires_clarification"):
            status = HomeControlStatus.UNSUPPORTED
        elif plan.blocked:
            status = HomeControlStatus.BLOCKED
        elif not plan.supported:
            status = HomeControlStatus.UNSUPPORTED
        elif plan.state_read:
            status = HomeControlStatus.STATE_READ
        else:
            status = HomeControlStatus.AWAITING_CONFIRMATION
        return HomeControlResult(
            plan_id=plan.plan_id,
            status=status,
            executed=False,
            dry_run=True,
            message=device_result.message if status is HomeControlStatus.UNSUPPORTED else plan.summary,
            state_before={},
            state_after={},
            data={"home_plan": plan},
            audit_metadata=dict(plan.audit_metadata),
        )

    def read_state_preview(self, device_id: str, capability: str) -> HomeControlResult:
        return HomeControlResult(
            plan_id=f"home-{uuid4().hex[:12]}",
            status=HomeControlStatus.STATE_READ,
            executed=False,
            dry_run=True,
            message=f"{device_id} icin {capability} state-read preview hazir.",
            audit_metadata={
                "execution_attempted": False,
                "network_used": False,
                "physical_device_touched": False,
            },
        )

    def summarize_plan(self, plan: HomeControlPlan) -> str:
        return plan.summary
