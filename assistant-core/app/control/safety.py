from app.control.models import PCControlRequest, PCActionCapability
from app.actions.types import ActionSource, PermissionStatus
from app.actions.risk import RiskLevel
from app.control.registry import get_capability

def is_safe_to_plan(request: PCControlRequest) -> bool:
    action = request.action
    decision = request.permission_decision
    
    if decision.blocked or decision.requires_clarification:
        return False
        
    if action.risk_level == RiskLevel.BLOCKED:
        return False
        
    capability = get_capability(action.action_type)
    if not capability.supported:
        return False
        
    if capability.risk_level == RiskLevel.BLOCKED:
        return False
        
    return True

def is_safe_to_execute(request: PCControlRequest, plan_capability: PCActionCapability) -> tuple[bool, str]:
    if request.dry_run:
        return False, "dry_run enabled"
        
    if not request.execute:
        return False, "execute flag not set"
        
    if not plan_capability.execution_supported:
        return False, "action execution not supported in MVP"
        
    decision = request.permission_decision
    if decision.blocked:
        return False, "permission blocked"
        
    if not decision.allowed_to_execute and decision.status != PermissionStatus.SAFE_READONLY:
        return False, "execution not allowed by permission manager"
        
    if plan_capability.risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH}:
        return False, "medium/high risk action execution not supported in MVP"
        
    if request.source == ActionSource.VOICE and plan_capability.risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH}:
        return False, "voice source medium/high risk action execution not supported"
        
    target = getattr(request.action, "target", "")
    if not target and plan_capability.action_type != "pc.system_info":
        return False, "target cannot be empty for this action"
        
    # Extra shell/arbitrary check
    target_str = str(target)
    if " " in target_str and ("-" in target_str or "/" in target_str) and plan_capability.action_type not in {"browser.search", "file.search"}:
        return False, "arbitrary command arguments detected in target"
        
    return True, ""
