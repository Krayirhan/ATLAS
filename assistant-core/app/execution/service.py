from __future__ import annotations

from uuid import uuid4

from app.actions.intent_router import IntentRouter
from app.actions.types import ActionSource
from app.execution.allowlist import ExecutionAllowlist
from app.execution.gate import SafeExecutionGate
from app.execution.models import ExecutionEligibility, ExecutionMode, ExecutionPlan, ExecutionRequest, ExecutionResult
from app.execution.policy import mode_from_text
from app.panel.store import LocalJsonPanelStore


class ExecutionService:
    def __init__(self, project_name: str = "ATLAS", *, panel_store=None) -> None:
        self.project_name = project_name
        self.router = IntentRouter()
        self.allowlist = ExecutionAllowlist()
        self.gate = SafeExecutionGate(self.allowlist)
        self.panel_store = panel_store or LocalJsonPanelStore()

    def from_text(self, text: str, *, mode: ExecutionMode | str | None = None, source: ActionSource = ActionSource.TEXT) -> ExecutionPlan:
        preview = self.router.preview(text, source=source)
        requested_mode = mode_from_text(mode.value if isinstance(mode, ExecutionMode) else mode)
        request = ExecutionRequest(
            request_id=f"req-{uuid4().hex[:12]}",
            source=source.value,
            action_candidate=preview.action_candidate,
            permission_decision=preview.permission_decision,
            requested_mode=requested_mode,
            user_confirmed=False,
            metadata={
                "raw_text": text,
                "action_type": getattr(getattr(preview, "intent", None), "action_candidate", None),
                "target": getattr(getattr(preview, "intent", None), "target", ""),
                "risk_level": getattr(getattr(preview.action_candidate, "risk_level", None), "value", "unknown")
                if preview.action_candidate
                else "unknown",
                "permission_status": getattr(getattr(preview.permission_decision, "status", None), "value", "unknown")
                if preview.permission_decision
                else "unknown",
            },
        )
        return self.gate.build_plan(request)

    def from_panel_item(self, item_id: str, *, mode: ExecutionMode | str | None = None) -> ExecutionPlan:
        item = self.panel_store.get(item_id)
        requested_mode = mode_from_text(mode.value if isinstance(mode, ExecutionMode) else mode)
        if item is None:
            request = ExecutionRequest(
                request_id=f"req-{uuid4().hex[:12]}",
                source="panel",
                requested_mode=requested_mode,
                metadata={"panel_status": "missing", "action_type": "", "target": ""},
            )
            return self.gate.build_plan(request)
        request = ExecutionRequest(
            request_id=f"req-{uuid4().hex[:12]}",
            source=item.source or "panel",
            permission_decision=item.permission_decision,
            panel_item=item,
            requested_mode=requested_mode,
            user_confirmed=bool(item.last_decision and getattr(item.last_decision.decision, "value", "") == "approve"),
            metadata={
                "action_type": item.action_type,
                "target": item.target,
                "risk_level": item.risk_level or "unknown",
                "panel_status": item.status.value,
                "panel_type": item.item_type.value,
                "permission_status": str(item.permission_decision.get("status", "unknown")) if isinstance(item.permission_decision, dict) else "unknown",
            },
        )
        return self.gate.build_plan(request)

    def evaluate_pc_action(self, text: str, *, source: ActionSource = ActionSource.TEXT) -> ExecutionEligibility:
        preview = self.router.preview(text, source=source)
        request = ExecutionRequest(
            request_id=f"req-{uuid4().hex[:12]}",
            source=source.value,
            action_candidate=preview.action_candidate,
            permission_decision=preview.permission_decision,
            metadata={
                "action_type": getattr(getattr(preview, "intent", None), "action_candidate", None),
                "target": getattr(getattr(preview, "intent", None), "target", ""),
                "risk_level": getattr(getattr(preview.action_candidate, "risk_level", None), "value", "unknown")
                if preview.action_candidate
                else "unknown",
                "permission_status": getattr(getattr(preview.permission_decision, "status", None), "value", "unknown")
                if preview.permission_decision
                else "unknown",
            },
        )
        return self.gate.evaluate(request)

    def execute_plan(self, plan: ExecutionPlan) -> ExecutionResult:
        return self.gate.execute(plan)

    def check_allowlist(self, action_type: str) -> dict[str, object]:
        policy = self.allowlist.get_policy(action_type)
        return {
            "action_type": action_type,
            "allowed": self.allowlist.is_action_allowed(action_type),
            "policy": policy,
            "explanation": self.allowlist.explain(action_type),
        }

    def format_result(self, plan: ExecutionPlan, result: ExecutionResult) -> dict[str, object]:
        return {
            "project": self.project_name,
            "plan": plan.model_dump(mode="json"),
            "result": result.model_dump(mode="json"),
        }

