from app.routines.models import (
    RoutineDefinition, RoutinePreview, RoutineStatus, RoutineCategory,
    RoutineSource, RoutineStepResult, RoutineResult
)
from app.routines.templates import get_builtin_templates
from app.routines.policy import RoutinePolicy
from app.actions.types import ActionType, ActionSource, IntentCategory
from app.actions.risk import RiskLevel
from app.actions.models import ActionCandidate
import uuid
from app.actions.permission import PermissionManager
from app.personal_memory.service import PersonalMemoryService
from app.personal_memory.models import MemoryType

class RoutineEngine:
    def __init__(self):
        self.templates = get_builtin_templates()
        self.custom_routines: list[RoutineDefinition] = []
        self.permission_manager = PermissionManager()
        self.memory_service = PersonalMemoryService()

    def list_templates(self) -> list[RoutineDefinition]:
        return self.templates
        
    def list_routines(self) -> list[RoutineDefinition]:
        return self.templates + self.custom_routines

    def get_template(self, name_or_alias: str) -> RoutineDefinition | None:
        target = name_or_alias.lower().replace(" modunu", " modu")
        target = target.replace(" moduna", " modu")
        
        for t in self.list_routines():
            if t.name.lower() in target:
                return t
        return None

    def _apply_memory_preferences(self, routine: RoutineDefinition):
        # Optional MVP PersonalMemory integration
        # Fetch preferences to replace generic targets
        prefs = self.memory_service.store.list_all(MemoryType.PREFERENCE)
        pref_dict = {p.key.lower(): p.value for p in prefs}
        
        # e.g., if "Chrome kullanırım" was recorded, replace pc.open_app target with Chrome if it was generic
        for step in routine.steps:
            if step.action_type == "pc.open_app" and step.target in ["VS Code", "Steam", "Spotify"]:
                # Very basic overriding logic for MVP
                for p_key, p_val in pref_dict.items():
                    if "kullanırım" in p_val.lower() or "severim" in p_val.lower():
                        # Extract app name naively
                        app_name = p_val.split(" ")[0]
                        if app_name.lower() not in ["bunu", "şunu", "oyun"]:
                            step.target = app_name.capitalize()
                            break

    def preview_routine(self, name_or_alias: str, source: ActionSource = ActionSource.TEXT) -> RoutinePreview:
        routine = self.get_template(name_or_alias)
        if not routine:
            return RoutinePreview(
                routine_id="unknown",
                routine_name=name_or_alias,
                summary="Bilinmeyen rutin.",
                steps=[],
                risk_level="unknown",
                requires_confirmation=False,
                blocked=True,
                blocked_reason="Rutin bulunamadı.",
                permission_decisions={},
                safe_to_run=False,
                estimated_effect="None"
            )
            
        # Copy routine to avoid modifying template during memory application
        import copy
        routine_copy = copy.deepcopy(routine)
        self._apply_memory_preferences(routine_copy)

        decisions = {}
        for step in routine_copy.steps:
            # Map string action_type to ActionType Enum
            try:
                a_type = ActionType(step.action_type)
            except ValueError:
                # Use a generic fallback if string isn't an exact match (e.g. routine.note)
                a_type = ActionType.ROUTINE_RUN if "routine" in step.action_type else ActionType.UNKNOWN
            
            risk = RiskLevel(step.risk_level) if hasattr(RiskLevel, step.risk_level.upper()) else RiskLevel.LOW
            candidate = ActionCandidate(
                action_id=str(uuid.uuid4()),
                action_type=a_type,
                target=step.target or "",
                parameters=step.parameters,
                source=source,
                user_goal=f"Execute routine step: {step.label}",
                intent_category=IntentCategory.ROUTINE_RUN,
                risk_level=risk,
                requires_confirmation=step.requires_confirmation or risk in [RiskLevel.MEDIUM, RiskLevel.HIGH],
                dry_run_supported=step.dry_run_supported,
                reversible=False,
                expected_result=step.expected_result or "Step executed"
            )
            decision = self.permission_manager.decide(candidate)
            decisions[step.step_id] = decision
            
        agg_risk, req_conf, is_blocked = RoutinePolicy.evaluate_routine(routine_copy, decisions)
        
        # If any step is missing target and it's not optional, safe_to_run is false
        safe_to_run = not is_blocked
        for step in routine_copy.steps:
            if not step.target and not step.parameters and not step.optional:
                # some actions might be valid without targets like mute_toggle
                if "toggle" not in step.action_type:
                    safe_to_run = False
                    
        return RoutinePreview(
            routine_id=routine_copy.routine_id,
            routine_name=routine_copy.name,
            summary=routine_copy.description,
            steps=routine_copy.steps,
            risk_level=agg_risk,
            requires_confirmation=req_conf,
            blocked=is_blocked,
            blocked_reason="Bir veya daha fazla adım yasaklı." if is_blocked else None,
            permission_decisions=decisions,
            safe_to_run=safe_to_run,
            estimated_effect=f"Dry run of {len(routine_copy.steps)} steps."
        )

    def run_routine(self, name_or_alias: str, dry_run: bool = True) -> RoutineResult:
        # MVP: ALWAYS dry_run=True and executed=False
        preview = self.preview_routine(name_or_alias)
        
        if preview.blocked:
            return RoutineResult(
                routine_id=preview.routine_id,
                status=RoutineStatus.BLOCKED,
                executed=False,
                dry_run=True,
                message=f"Rutin engellendi: {preview.blocked_reason}",
                blocked_reason=preview.blocked_reason
            )
            
        if preview.requires_confirmation:
            return RoutineResult(
                routine_id=preview.routine_id,
                status=RoutineStatus.AWAITING_CONFIRMATION,
                executed=False,
                dry_run=True,
                message=f"'{preview.routine_name}' rutini onay bekliyor. Risk seviyesi: {preview.risk_level}.",
            )
            
        return RoutineResult(
            routine_id=preview.routine_id,
            status=RoutineStatus.PREVIEWED,
            executed=False,
            dry_run=True,
            message=f"'{preview.routine_name}' rutini güvenli. Dry-run modunda çalıştırılabilir.",
        )
