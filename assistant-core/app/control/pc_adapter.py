import platform
from app.actions.models import ActionCandidate, PermissionDecision
from app.control.models import (
    PCControlRequest, PCControlPlan, PCControlResult, PCControlStatus
)
from app.control.registry import get_capability
from app.control.safety import is_safe_to_plan, is_safe_to_execute

class PCControlAdapter:
    def __init__(self):
        pass

    def supports(self, action_type: str) -> bool:
        return get_capability(action_type).supported

    def resolve_target(self, action: ActionCandidate) -> str:
        # In MVP, we just return the target directly without deep resolution
        return getattr(action, "target", "")

    def get_system_info(self) -> dict:
        return {
            "os": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }

    def build_plan(self, action: ActionCandidate, decision: PermissionDecision, dry_run: bool = True) -> PCControlPlan:
        request = PCControlRequest(
            action=action,
            permission_decision=decision,
            dry_run=dry_run,
            execute=not dry_run, # map execute flag for safety checks
            user_goal=action.user_goal,
            source=action.source
        )
        
        capability = get_capability(action.action_type)
        resolved_target = self.resolve_target(action)
        
        if not is_safe_to_plan(request):
            return PCControlPlan(
                action_id=action.action_id,
                action_type=action.action_type,
                target=action.target,
                resolved_target=resolved_target,
                capability=capability,
                dry_run=dry_run,
                executable=False,
                execution_allowed=False,
                risk_level=capability.risk_level,
                requires_confirmation=decision.requires_confirmation,
                summary=f"Blocked or unsupported action: {action.action_type}",
                blocked_reason=decision.reason or "Blocked by safety gate",
                warnings=["This action cannot be planned."]
            )
            
        executable = capability.execution_supported
        execution_allowed, blocked_reason = is_safe_to_execute(request, capability)
        
        summary = f"Plan for {action.action_type}"
        if resolved_target:
            summary += f" on {resolved_target}"
            
        if dry_run:
            summary += " (dry-run)"
            
        return PCControlPlan(
            action_id=action.action_id,
            action_type=action.action_type,
            target=action.target,
            resolved_target=resolved_target,
            capability=capability,
            dry_run=dry_run,
            executable=executable,
            execution_allowed=execution_allowed,
            risk_level=capability.risk_level,
            requires_confirmation=decision.requires_confirmation,
            summary=summary,
            blocked_reason=blocked_reason,
            audit_metadata={"planned": True}
        )

    def execute(self, plan: PCControlPlan) -> PCControlResult:
        if plan.blocked_reason or not plan.executable:
            # Check if it was merely unsupported for execution but supported for dry-run
            if plan.dry_run and not plan.blocked_reason and plan.capability.dry_run_supported:
                return PCControlResult(
                    action_id=plan.action_id,
                    status=PCControlStatus.PREVIEWED,
                    executed=False,
                    dry_run=True,
                    message=f"Dry run complete for {plan.action_type}"
                )
            
            status = PCControlStatus.BLOCKED if plan.blocked_reason else PCControlStatus.UNSUPPORTED
            return PCControlResult(
                action_id=plan.action_id,
                status=status,
                executed=False,
                dry_run=plan.dry_run,
                message=f"Execution blocked or unsupported: {plan.blocked_reason or 'Not supported'}",
                error_message=plan.blocked_reason
            )
            
        if plan.dry_run:
            return PCControlResult(
                action_id=plan.action_id,
                status=PCControlStatus.PREVIEWED,
                executed=False,
                dry_run=True,
                message=f"Dry run complete for {plan.action_type}"
            )
            
        if not plan.execution_allowed:
            return PCControlResult(
                action_id=plan.action_id,
                status=PCControlStatus.BLOCKED,
                executed=False,
                dry_run=plan.dry_run,
                message="Execution not allowed by safety gate"
            )
            
        # MVP: Only pc.system_info is executed
        if plan.action_type == "pc.system_info":
            info = self.get_system_info()
            return PCControlResult(
                action_id=plan.action_id,
                status=PCControlStatus.EXECUTED,
                executed=True,
                dry_run=False,
                message="System info retrieved",
                data=info,
                audit_metadata={"execution_attempted": True}
            )
            
        # Anything else that reaches here in MVP is ready but not executed
        return PCControlResult(
            action_id=plan.action_id,
            status=PCControlStatus.READY,
            executed=False,
            dry_run=plan.dry_run,
            message=f"Action {plan.action_type} ready but real execution is not implemented in MVP"
        )
