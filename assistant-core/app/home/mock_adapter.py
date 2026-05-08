from __future__ import annotations

from app.actions.risk import RiskLevel
from app.devices.models import DeviceActionPlan, DeviceState
from app.devices.registry import DeviceRegistry
from app.home.models import (
    HomeAdapterCapability,
    HomeControlPlan,
    HomeControlResult,
    HomeControlStatus,
    HomeStateReadRequest,
    HomeStateReadResult,
    HomeStateWriteRequest,
    HomeStateWriteResult,
)
from app.home.planner import HomeControlPlanner


class MockHomeControlAdapter:
    def __init__(self, *, registry: DeviceRegistry | None = None) -> None:
        self.registry = registry or DeviceRegistry()

    def name(self) -> str:
        return "mock_home_control"

    def health_check(self) -> dict[str, object]:
        return {
            "ok": True,
            "adapter": self.name(),
            "network_used": False,
            "physical_device_touched": False,
            "execution_supported": False,
        }

    def capabilities(self) -> list[HomeAdapterCapability]:
        return [
            HomeAdapterCapability(self.name(), "state_query", True, False, False, True, RiskLevel.SAFE_READONLY, ["mock-only"]),
            HomeAdapterCapability(self.name(), "power", False, True, False, True, RiskLevel.MEDIUM, ["write disabled"]),
            HomeAdapterCapability(self.name(), "brightness", False, True, False, True, RiskLevel.MEDIUM, ["write disabled"]),
            HomeAdapterCapability(self.name(), "temperature", False, True, False, True, RiskLevel.MEDIUM, ["write disabled"]),
        ]

    def build_plan(self, device_action_plan: DeviceActionPlan) -> HomeControlPlan:
        planner = HomeControlPlanner(adapter_name=self.name())
        return planner.build_plan(device_action_plan)

    def read_state(self, request: HomeStateReadRequest) -> HomeStateReadResult:
        device = self.registry.get_device(request.device_id)
        state = device.state if device and device.state else DeviceState(device_id=request.device_id)
        value = getattr(state, self._state_attr(request.capability), None)
        return HomeStateReadResult(
            device_id=request.device_id,
            capability=request.capability,
            supported=True,
            value=value,
            stale=False,
            source="mock_registry_state",
            message=f"{request.device_id} icin mock state-read sonucu.",
            metadata={"network_used": False, "physical_device_touched": False, "execution_attempted": False},
        )

    def write_state(self, request: HomeStateWriteRequest) -> HomeStateWriteResult:
        return HomeStateWriteResult(
            device_id=request.device_id,
            capability=request.capability,
            accepted=request.requires_confirmation,
            executed=False,
            dry_run=True,
            message=f"{request.device_id} icin mock state-write preview. Gercek cihaz degismedi.",
            metadata={"network_used": False, "physical_device_touched": False, "execution_attempted": False},
        )

    def execute(self, plan: HomeControlPlan) -> HomeControlResult:
        if plan.state_read:
            state = self.read_state(HomeStateReadRequest(device_id=plan.device_id, capability=plan.capability))
            return HomeControlResult(
                plan_id=plan.plan_id,
                status=HomeControlStatus.STATE_READ,
                executed=False,
                dry_run=True,
                message=state.message,
                state_before={"value": state.value},
                data={"state_read": state},
                audit_metadata={**plan.audit_metadata, "network_used": False, "physical_device_touched": False, "execution_attempted": False},
            )
        if plan.audit_metadata.get("requires_clarification"):
            status = HomeControlStatus.UNSUPPORTED
            message = plan.blocked_reason or "Home control target clarification gerekli."
        elif plan.blocked:
            status = HomeControlStatus.BLOCKED
            message = plan.blocked_reason
        elif not plan.supported:
            status = HomeControlStatus.UNSUPPORTED
            message = plan.blocked_reason or "Home control action MVP policy tarafindan unsupported."
        else:
            status = HomeControlStatus.AWAITING_CONFIRMATION
            message = f"{plan.device_id} icin mock home write preview hazir. Gercek execution yok."
        return HomeControlResult(
            plan_id=plan.plan_id,
            status=status,
            executed=False,
            dry_run=True,
            message=message,
            audit_metadata={**plan.audit_metadata, "network_used": False, "physical_device_touched": False, "execution_attempted": False},
        )

    def _state_attr(self, capability: str) -> str:
        mapping = {
            "state_query": "power_state",
            "power": "power_state",
            "brightness": "brightness",
            "temperature": "temperature",
            "mode": "mode",
        }
        return mapping.get(capability, "power_state")
