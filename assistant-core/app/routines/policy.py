from app.routines.models import RoutineDefinition, RoutinePreview, RoutineStatus
from app.actions.types import ActionType, ActionSource, PermissionStatus

class RoutinePolicy:
    
    @classmethod
    def evaluate_routine(cls, routine: RoutineDefinition, permission_decisions: dict) -> tuple[str, bool, bool]:
        """Returns: (aggregated_risk_level, requires_confirmation, blocked)"""
        has_blocked = False
        has_high = False
        has_medium = False
        has_home_device = False
        
        for step in routine.steps:
            if "device" in step.action_type:
                has_home_device = True
            
            if step.action_type in ["pc.shutdown", "pc.lock"]:
                has_high = True
                
            decision = permission_decisions.get(step.step_id)
            if decision:
                if decision.status == PermissionStatus.BLOCKED:
                    has_blocked = True
                if decision.status == PermissionStatus.CONFIRMATION_REQUIRED:
                    # Inherit risk if available, else assume medium or high
                    if step.risk_level == "high":
                        has_high = True
                    else:
                        has_medium = True
                        
            # Use step's own defined risk level as a baseline
            if step.risk_level == "high":
                has_high = True
            elif step.risk_level == "medium":
                has_medium = True
                
        if has_home_device:
            has_medium = True
            
        is_blocked = has_blocked
        requires_confirmation = (
            has_high
            or has_medium
            or routine.requires_confirmation
            or routine.risk_level in {"medium", "high"}
        )
        
        agg_risk = "low"
        if has_high or routine.risk_level == "high":
            agg_risk = "high"
        elif has_medium or routine.risk_level == "medium":
            agg_risk = "medium"
            
        return agg_risk, requires_confirmation, is_blocked
