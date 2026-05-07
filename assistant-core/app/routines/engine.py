import copy
import uuid

from app.actions.models import ActionCandidate
from app.actions.permission import PermissionManager
from app.actions.risk import RiskLevel
from app.actions.types import ActionSource, ActionType, IntentCategory
from app.personal_memory.models import MemoryType
from app.personal_memory.service import PersonalMemoryService
from app.routines.models import RoutineDefinition, RoutinePreview, RoutineResult, RoutineStatus, RoutineStepResult
from app.routines.policy import RoutinePolicy
from app.routines.templates import get_builtin_templates


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

    def create_custom_routine(self, definition: RoutineDefinition) -> RoutineDefinition:
        self.custom_routines.append(definition)
        return definition

    def get_template(self, name_or_alias: str) -> RoutineDefinition | None:
        target = self._normalize_name(name_or_alias).replace(" modunu", " modu").replace(" moduna", " modu")
        for routine in self.list_routines():
            if self._normalize_name(routine.name) in target:
                return routine
        return None

    def _normalize_name(self, value: str) -> str:
        normalized = value.lower()
        translations = str.maketrans(
            {
                "ç": "c",
                "ğ": "g",
                "ı": "i",
                "ö": "o",
                "ş": "s",
                "ü": "u",
            }
        )
        return normalized.translate(translations)

    def _apply_memory_preferences(self, routine: RoutineDefinition) -> None:
        prefs = self.memory_service.store.list_all(MemoryType.PREFERENCE)
        pref_dict = {item.key.lower(): str(item.value) for item in prefs}

        for step in routine.steps:
            if step.action_type != "pc.open_app" or step.target not in ["VS Code", "Steam", "Spotify"]:
                continue
            for _, pref_value in pref_dict.items():
                lowered = pref_value.lower()
                if "kullan" not in lowered and "sever" not in lowered:
                    continue
                app_name = pref_value.split(" ")[0]
                if app_name.lower() not in {"bunu", "sunu", "oyun"}:
                    step.target = app_name.capitalize()
                    break

    def _build_step_candidate(self, step, source: ActionSource) -> ActionCandidate:
        try:
            action_type = ActionType(step.action_type)
        except ValueError:
            action_type = ActionType.ROUTINE_PREVIEW if "routine" in step.action_type else ActionType.ROUTINE_RUN

        try:
            risk_level = RiskLevel(step.risk_level)
        except ValueError:
            risk_level = RiskLevel.LOW

        return ActionCandidate(
            action_id=str(uuid.uuid4()),
            action_type=action_type,
            target=step.target or "",
            parameters=step.parameters,
            source=source,
            user_goal=f"Preview routine step: {step.label}",
            intent_category=IntentCategory.ROUTINE_RUN,
            risk_level=risk_level,
            requires_confirmation=step.requires_confirmation or risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH},
            dry_run_supported=step.dry_run_supported,
            reversible=False,
            expected_result=step.expected_result or "Preview only; no execution in Sprint 43.",
            audit_metadata={"routine_step_id": step.step_id, "execution_attempted": False},
        )

    def _preview_audit_metadata(self, routine: RoutineDefinition, risk_level: str, blocked: bool) -> dict[str, object]:
        return {
            "routine_id": routine.routine_id,
            "routine_name": routine.name,
            "risk_level": risk_level,
            "blocked": blocked,
            "execution_attempted": False,
        }

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
                blocked_reason="Rutin bulunamadi.",
                permission_decisions={},
                safe_to_run=False,
                estimated_effect="None",
                audit_metadata={"execution_attempted": False, "blocked": True},
            )

        routine_copy = copy.deepcopy(routine)
        self._apply_memory_preferences(routine_copy)

        decisions = {}
        for step in routine_copy.steps:
            candidate = self._build_step_candidate(step, source)
            decisions[step.step_id] = self.permission_manager.decide(candidate)

        aggregate_risk, requires_confirmation, is_blocked = RoutinePolicy.evaluate_routine(routine_copy, decisions)

        safe_to_run = not is_blocked
        for step in routine_copy.steps:
            if step.optional:
                continue
            if not step.target and not step.parameters and "toggle" not in step.action_type:
                safe_to_run = False

        return RoutinePreview(
            routine_id=routine_copy.routine_id,
            routine_name=routine_copy.name,
            summary=routine_copy.description,
            steps=routine_copy.steps,
            risk_level=aggregate_risk,
            requires_confirmation=requires_confirmation,
            blocked=is_blocked,
            blocked_reason="Bir veya daha fazla adim yasakli." if is_blocked else None,
            permission_decisions=decisions,
            safe_to_run=safe_to_run,
            estimated_effect=f"Dry run of {len(routine_copy.steps)} steps.",
            audit_metadata=self._preview_audit_metadata(routine_copy, aggregate_risk, is_blocked),
        )

    def run_routine(self, name_or_alias: str, dry_run: bool = True) -> RoutineResult:
        preview = self.preview_routine(name_or_alias)
        step_results = [
            RoutineStepResult(
                step_id=step.step_id,
                status=preview.permission_decisions[step.step_id].status.value if step.step_id in preview.permission_decisions else "unknown",
                executed=False,
                message="Preview only; Sprint 43 does not execute routine steps.",
                permission_decision=preview.permission_decisions.get(step.step_id),
                audit_metadata={"execution_attempted": False, "routine_id": preview.routine_id},
            )
            for step in preview.steps
        ]

        if preview.blocked:
            return RoutineResult(
                routine_id=preview.routine_id,
                status=RoutineStatus.BLOCKED,
                executed=False,
                dry_run=True,
                message=f"Rutin engellendi: {preview.blocked_reason}",
                step_results=step_results,
                blocked_reason=preview.blocked_reason,
                audit_metadata={"execution_attempted": False, "routine_id": preview.routine_id, "status": "blocked"},
            )

        if preview.requires_confirmation:
            return RoutineResult(
                routine_id=preview.routine_id,
                status=RoutineStatus.AWAITING_CONFIRMATION,
                executed=False,
                dry_run=True,
                message=f"'{preview.routine_name}' rutini onay bekliyor. Risk seviyesi: {preview.risk_level}.",
                step_results=step_results,
                audit_metadata={
                    "execution_attempted": False,
                    "routine_id": preview.routine_id,
                    "status": "awaiting_confirmation",
                },
            )

        return RoutineResult(
            routine_id=preview.routine_id,
            status=RoutineStatus.PREVIEWED,
            executed=False,
            dry_run=True,
            message=f"'{preview.routine_name}' rutini guvenli. Dry-run modunda calistirilabilir.",
            step_results=step_results,
            audit_metadata={"execution_attempted": False, "routine_id": preview.routine_id, "status": "previewed"},
        )
