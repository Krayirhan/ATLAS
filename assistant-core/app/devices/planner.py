from __future__ import annotations

from app.actions import ActionCandidate, ActionSource, ActionType, IntentRouter, PermissionManager
from app.actions.risk import RiskLevel
from app.devices.capabilities import device_supports, get_capability_rule
from app.devices.models import DeviceActionPlan, DeviceRegistryResult, DeviceRegistryStatus
from app.devices.policy import plan_from_resolution
from app.devices.registry import DeviceRegistry
from app.devices.resolver import DeviceTargetResolver


class DeviceActionPlanner:
    def __init__(
        self,
        *,
        registry: DeviceRegistry | None = None,
        resolver: DeviceTargetResolver | None = None,
        permission_manager: PermissionManager | None = None,
        router: IntentRouter | None = None,
    ) -> None:
        self.registry = registry or DeviceRegistry()
        self.resolver = resolver or DeviceTargetResolver(self.registry)
        self.permission_manager = permission_manager or PermissionManager()
        self.router = router or IntentRouter(permission_manager=self.permission_manager)

    def build_plan(self, action: ActionCandidate) -> DeviceActionPlan:
        resolution = self.resolver.resolve_action(action)
        if resolution.metadata.get("blocked"):
            return plan_from_resolution(
                action=action,
                resolution=resolution,
                capability="",
                risk_level=RiskLevel.BLOCKED,
                requires_confirmation=False,
                supported=False,
                blocked=True,
                blocked_reason=resolution.ambiguity_reason,
                warnings=list(resolution.warnings),
                summary=resolution.ambiguity_reason,
            )
        if resolution.requires_clarification or not resolution.resolved or resolution.device is None:
            return plan_from_resolution(
                action=action,
                resolution=resolution,
                capability="",
                risk_level=action.risk_level,
                requires_confirmation=False,
                supported=False,
                blocked=False,
                clarification_required=True,
                warnings=list(resolution.warnings),
                summary=resolution.ambiguity_reason or "Device target clarification gerekli.",
            )

        rule = get_capability_rule(action.action_type)
        if rule is None:
            return plan_from_resolution(
                action=action,
                resolution=resolution,
                capability="",
                risk_level=RiskLevel.BLOCKED,
                requires_confirmation=False,
                supported=False,
                blocked=True,
                blocked_reason="Bu cihaz aksiyonu planner tarafinda desteklenmiyor.",
                summary="Unsupported device action.",
            )

        if rule.blocked:
            return plan_from_resolution(
                action=action,
                resolution=resolution,
                capability=rule.required_capability.value,
                risk_level=RiskLevel.BLOCKED,
                requires_confirmation=False,
                supported=False,
                blocked=True,
                blocked_reason=rule.unsupported_reason,
                warnings=list(rule.warnings),
                summary=rule.unsupported_reason,
            )

        capability = device_supports(resolution.device, rule.required_capability)
        if capability is None:
            return plan_from_resolution(
                action=action,
                resolution=resolution,
                capability=rule.required_capability.value,
                risk_level=RiskLevel.BLOCKED,
                requires_confirmation=False,
                supported=False,
                blocked=True,
                blocked_reason=f"{resolution.device.display_name} cihazinda {rule.required_capability.value} capability yok.",
                summary="Capability unsupported.",
            )

        decision = self.permission_manager.decide(action)
        summary = (
            f"{resolution.device.display_name} icin {action.action_type.value} action'i preview edildi. "
            "Gercek home control execution henuz yok."
        )
        return plan_from_resolution(
            action=action,
            resolution=resolution,
            capability=capability.capability.value,
            risk_level=rule.risk_level,
            requires_confirmation=decision.requires_confirmation or rule.requires_confirmation,
            supported=True,
            blocked=False,
            warnings=list(decision.warnings),
            summary=summary,
        )

    def build_plan_from_text(self, text: str, source: ActionSource = ActionSource.TEXT) -> DeviceActionPlan | None:
        preview = self.router.preview(text, source=source)
        if preview.action_candidate is None:
            return None
        return self.build_plan(preview.action_candidate)

    def preview_device_action(self, text: str, source: ActionSource = ActionSource.TEXT) -> DeviceRegistryResult:
        preview = self.router.preview(text, source=source)
        if preview.action_candidate is None:
            resolution = self.resolver.resolve_text(text)
            status = DeviceRegistryStatus.AMBIGUOUS if resolution.requires_clarification else DeviceRegistryStatus.UNRESOLVED
            message = resolution.ambiguity_reason or "Device target cozulmedi."
            return DeviceRegistryResult(
                status=status,
                message=message,
                resolution=resolution,
                warnings=list(resolution.warnings),
                metadata={"execution_attempted": False},
            )

        plan = self.build_plan(preview.action_candidate)
        resolution = self.resolver.resolve_action(preview.action_candidate)
        if plan.blocked:
            status = DeviceRegistryStatus.BLOCKED
        elif plan.clarification_required:
            status = DeviceRegistryStatus.AMBIGUOUS
        elif plan.supported:
            status = DeviceRegistryStatus.PLANNED
        else:
            status = DeviceRegistryStatus.UNSUPPORTED

        message = plan.summary or resolution.ambiguity_reason or "Device action preview hazir."
        return DeviceRegistryResult(
            status=status,
            message=message,
            device=resolution.device,
            room=resolution.room,
            resolution=resolution,
            plan=plan,
            warnings=list(plan.warnings),
            metadata={"execution_attempted": False},
        )
