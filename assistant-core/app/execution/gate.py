from __future__ import annotations

from uuid import uuid4

from app.execution.allowlist import BLOCKED_ACTION_TYPES, ExecutionAllowlist, normalize_target
from app.execution.audit import build_audit_metadata
from app.execution.models import (
    ExecutionEligibility,
    ExecutionPlan,
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
    RollbackPlan,
)
from app.execution.policy import (
    APPROVED_PANEL_STATUSES,
    APPROVED_PANEL_TYPES,
    BLOCKED_PANEL_STATUSES,
    BLOCKED_PERMISSION_STATUSES,
    EXECUTION_ENABLED_DEFAULT,
    EXPIRED_PANEL_STATUSES,
    NON_EXECUTABLE_MODES,
    NON_PC_EXECUTION_ACTION_TYPES,
    is_home_or_device_action,
)


class SafeExecutionGate:
    def __init__(self, allowlist: ExecutionAllowlist | None = None) -> None:
        self.allowlist = allowlist or ExecutionAllowlist()

    def evaluate(self, request: ExecutionRequest) -> ExecutionEligibility:
        action_type = self._action_type(request)
        target = self._target(request)
        risk_level = self._risk_level(request)
        permission_status = self._permission_status(request)
        panel_status = self._panel_status(request)
        panel_type = self._panel_type(request)
        has_panel_approval = panel_status in APPROVED_PANEL_STATUSES or panel_type in APPROVED_PANEL_TYPES
        requires_panel_approval = True
        warnings: list[str] = []
        blockers: list[str] = []

        allowed_by_allowlist = self.allowlist.is_action_allowed(action_type)
        allowed_by_policy = True

        if not action_type:
            allowed_by_policy = False
            blockers.append("Aksiyon tipi belirlenemedi.")
        if action_type in BLOCKED_ACTION_TYPES:
            allowed_by_policy = False
            blockers.append("Aksiyon tipi explicit blocked list icinde.")
        if is_home_or_device_action(action_type):
            allowed_by_policy = False
            blockers.append("Home/device fiziksel aksiyonlari PC execution icin uygun degil.")
        if action_type in NON_PC_EXECUTION_ACTION_TYPES:
            allowed_by_policy = False
            blockers.append("Reminder/calendar/notification/routine execution Sprint 52 kapsaminda degil.")
        if risk_level in {"medium", "high", "blocked"}:
            allowed_by_policy = False
            blockers.append(f"Risk seviyesi {risk_level} oldugu icin execution eligibility disi.")
        if permission_status in BLOCKED_PERMISSION_STATUSES:
            allowed_by_policy = False
            blockers.append(f"Permission decision execution icin uygun degil: {permission_status}.")
        if request.source == "voice":
            warnings.append("Voice kaynagi ek confirmation gerektirir.")
        if panel_status in BLOCKED_PANEL_STATUSES:
            allowed_by_policy = False
            blockers.append(f"Panel status execution handoff icin uygun degil: {panel_status}.")
        if panel_status in EXPIRED_PANEL_STATUSES:
            allowed_by_policy = False
            blockers.append("Panel approval suresi dolmus.")

        if allowed_by_allowlist and not self.allowlist.is_target_allowed(action_type, target):
            allowed_by_policy = False
            blockers.append("Target allowlist disinda veya tanimsiz.")

        eligible = allowed_by_policy and allowed_by_allowlist
        if eligible and not has_panel_approval:
            warnings.append("Panel approval olmadan execution handoff sadece planning seviyesinde kalir.")

        if blockers:
            reason = blockers[0]
        elif eligible:
            reason = "Dusuk riskli ve allowlist uyumlu; future execution icin planlanabilir."
        else:
            reason = "Execution policy tarafindan uygun bulunmadi."

        return ExecutionEligibility(
            eligible=eligible,
            allowed_by_policy=allowed_by_policy,
            allowed_by_allowlist=allowed_by_allowlist,
            requires_panel_approval=requires_panel_approval,
            has_panel_approval=has_panel_approval,
            risk_level=risk_level,
            action_type=action_type,
            target=normalize_target(target),
            reason=reason,
            warnings=warnings,
            blockers=blockers,
            metadata={
                "permission_status": permission_status,
                "panel_status": panel_status,
                "panel_type": panel_type,
            },
        )

    def build_plan(self, request: ExecutionRequest) -> ExecutionPlan:
        eligibility = self.evaluate(request)
        execution_id = f"exec-{uuid4().hex[:12]}"
        resolved_target = normalize_target(eligibility.target)
        approved = eligibility.has_panel_approval
        executable = eligibility.eligible and approved and EXECUTION_ENABLED_DEFAULT
        will_execute = executable and request.requested_mode not in NON_EXECUTABLE_MODES
        audit_metadata = build_audit_metadata(
            execution_id=execution_id,
            action_type=eligibility.action_type,
            target=resolved_target,
            source=request.source,
            risk_level=eligibility.risk_level,
            permission_status=eligibility.metadata.get("permission_status", "unknown"),
            panel_status=eligibility.metadata.get("panel_status", "none"),
            allowlist_decision="allowed" if eligibility.allowed_by_allowlist else "blocked",
            requested_mode=request.requested_mode.value,
        )
        warnings = list(eligibility.warnings)
        if eligibility.eligible and not approved:
            warnings.append("Panel onayi alinmadan executable olamaz.")
        if eligibility.eligible and approved and not EXECUTION_ENABLED_DEFAULT:
            warnings.append("Execution gate globally disabled; armed_for_future disinda runtime yok.")
        return ExecutionPlan(
            execution_id=execution_id,
            action_type=eligibility.action_type,
            target=eligibility.target,
            resolved_target=resolved_target,
            mode=request.requested_mode,
            eligible=eligibility.eligible,
            executable=executable,
            will_execute=will_execute,
            dry_run=request.requested_mode.value in {"dry_run", "preview_only", "disabled"},
            requires_approval=eligibility.requires_panel_approval,
            approved=approved,
            rollback_available=False,
            rollback_plan=RollbackPlan(
                available=False,
                description="Sprint 52 rollback modeli sozlesme seviyesinde tanimlidir; runtime uygulanmadi.",
                steps=[],
                limitations=["Gercek execution acik olmadigi icin rollback uygulanamaz."],
            ),
            warnings=warnings,
            blocked_reason="" if eligibility.eligible else eligibility.reason,
            audit_metadata=audit_metadata,
        )

    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        audit_metadata = dict(plan.audit_metadata)
        if not plan.eligible:
            status = ExecutionStatus.EXPIRED if audit_metadata.get("panel_status") == "expired" else ExecutionStatus.BLOCKED
            return ExecutionResult(
                execution_id=plan.execution_id,
                status=status,
                executed=False,
                dry_run=plan.dry_run,
                message=plan.blocked_reason or "Execution blocked.",
                error_code="execution_blocked",
                error_message=plan.blocked_reason,
                audit_metadata=audit_metadata,
            )
        if plan.approved and not EXECUTION_ENABLED_DEFAULT:
            return ExecutionResult(
                execution_id=plan.execution_id,
                status=ExecutionStatus.ARMED_FOR_FUTURE,
                executed=False,
                dry_run=plan.dry_run,
                message="Eligible and approved, but real execution is disabled. Armed for future only.",
                audit_metadata=audit_metadata,
            )
        return ExecutionResult(
            execution_id=plan.execution_id,
            status=ExecutionStatus.PREVIEWED,
            executed=False,
            dry_run=plan.dry_run,
            message="Execution preview generated. Gercek islem yapilmadi.",
            audit_metadata=audit_metadata,
        )

    def cancel(self, plan_or_id: ExecutionPlan | str) -> ExecutionResult:
        execution_id = plan_or_id.execution_id if isinstance(plan_or_id, ExecutionPlan) else str(plan_or_id)
        return ExecutionResult(
            execution_id=execution_id,
            status=ExecutionStatus.CANCELLED,
            executed=False,
            dry_run=True,
            message="Execution request cancelled. Gercek islem yapilmadi.",
            audit_metadata={"execution_id": execution_id, "real_execution_attempted": False, "shell_used": False},
        )

    def deny(self, plan_or_id: ExecutionPlan | str) -> ExecutionResult:
        execution_id = plan_or_id.execution_id if isinstance(plan_or_id, ExecutionPlan) else str(plan_or_id)
        return ExecutionResult(
            execution_id=execution_id,
            status=ExecutionStatus.DENIED,
            executed=False,
            dry_run=True,
            message="Execution request denied. Gercek islem yapilmadi.",
            audit_metadata={"execution_id": execution_id, "real_execution_attempted": False, "shell_used": False},
        )

    def _action_type(self, request: ExecutionRequest) -> str:
        for value in (
            getattr(getattr(request, "action_candidate", None), "action_type", None),
            request.metadata.get("action_type"),
            getattr(getattr(request, "panel_item", None), "action_type", None),
        ):
            if value:
                return getattr(value, "value", value)
        return ""

    def _target(self, request: ExecutionRequest) -> str:
        for value in (
            getattr(getattr(request, "action_candidate", None), "target", None),
            request.metadata.get("target"),
            getattr(getattr(request, "panel_item", None), "target", None),
        ):
            if value is not None:
                return str(value)
        return ""

    def _risk_level(self, request: ExecutionRequest) -> str:
        for value in (
            getattr(getattr(request, "action_candidate", None), "risk_level", None),
            request.metadata.get("risk_level"),
            getattr(getattr(request, "panel_item", None), "risk_level", None),
        ):
            if value:
                return getattr(value, "value", str(value))
        return "unknown"

    def _permission_status(self, request: ExecutionRequest) -> str:
        decision = request.permission_decision
        if decision is None:
            return str(request.metadata.get("permission_status", "unknown"))
        status = getattr(decision, "status", None)
        if status is not None:
            return getattr(status, "value", str(status))
        if isinstance(decision, dict):
            return str(decision.get("status", "unknown"))
        return "unknown"

    def _panel_status(self, request: ExecutionRequest) -> str:
        panel_item = request.panel_item
        if panel_item is None:
            return str(request.metadata.get("panel_status", "none"))
        status = getattr(panel_item, "status", None)
        if status is not None:
            return getattr(status, "value", str(status))
        return "none"

    def _panel_type(self, request: ExecutionRequest) -> str:
        panel_item = request.panel_item
        if panel_item is None:
            return str(request.metadata.get("panel_type", "none"))
        item_type = getattr(panel_item, "item_type", None)
        if item_type is not None:
            return getattr(item_type, "value", str(item_type))
        return "none"

