from __future__ import annotations

from dataclasses import asdict, is_dataclass
from uuid import uuid4

from app.actions.types import ActionSource
from app.conversation.loop import ConversationLoop
from app.conversation.models import ConversationResponse, ConversationResponseType
from app.home.service import HomeControlService
from app.panel.models import (
    PanelDecision,
    PanelDecisionType,
    PanelItemStatus,
    PanelItemType,
    PanelOperationResult,
    PanelOperationStatus,
    PermissionPanelItem,
    PermissionPanelState,
)
from app.panel.policy import can_approve, default_expiry, sanitize_text, sanitize_value
from app.panel.store import InMemoryPanelStore, LocalJsonPanelStore


def _to_dict(value):
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if is_dataclass(value):
        return asdict(value)
    return sanitize_value(value)


class PermissionPanelService:
    def __init__(self, store=None) -> None:
        self.store = store or LocalJsonPanelStore()
        self.loop = ConversationLoop()
        self.home_service = HomeControlService()

    def create_from_conversation(self, response: ConversationResponse) -> PermissionPanelItem | None:
        response_type = response.response_type
        if response_type not in {
            ConversationResponseType.ACTION_PREVIEW,
            ConversationResponseType.CONFIRMATION_REQUIRED,
            ConversationResponseType.CLARIFICATION,
            ConversationResponseType.BLOCKED,
        }:
            return None

        item_type = {
            ConversationResponseType.ACTION_PREVIEW: PanelItemType.ACTION_PREVIEW,
            ConversationResponseType.CONFIRMATION_REQUIRED: PanelItemType.CONFIRMATION_REQUIRED,
            ConversationResponseType.CLARIFICATION: PanelItemType.CLARIFICATION_REQUIRED,
            ConversationResponseType.BLOCKED: PanelItemType.BLOCKED,
        }[response_type]
        status = {
            PanelItemType.BLOCKED: PanelItemStatus.BLOCKED,
            PanelItemType.CLARIFICATION_REQUIRED: PanelItemStatus.PENDING,
            PanelItemType.CONFIRMATION_REQUIRED: PanelItemStatus.PENDING,
            PanelItemType.ACTION_PREVIEW: PanelItemStatus.PENDING,
        }[item_type]

        action_type = ""
        target = ""
        risk_level = ""
        source = response.metadata.get("source", "text")
        assistant_metadata = response.metadata.get("personal_assistant", {})
        permission_decision = _to_dict(response.permission_decision)
        if response.action_candidate is not None:
            action_type = getattr(response.action_candidate.action_type, "value", str(response.action_candidate.action_type))
            target = response.action_candidate.target
            risk_level = getattr(response.action_candidate.risk_level, "value", str(response.action_candidate.risk_level))
            source = getattr(response.action_candidate.source, "value", str(response.action_candidate.source))
        elif response.permission_decision is not None:
            risk_level = getattr(response.permission_decision.risk_level, "value", str(response.permission_decision.risk_level))
        elif assistant_metadata:
            action_type = assistant_metadata.get("scope", "") + "." + assistant_metadata.get("operation", "")
            target = assistant_metadata.get("target", "")
            risk_level = assistant_metadata.get("risk_level", "")
            source = response.metadata.get("source", source)

        title = {
            PanelItemType.ACTION_PREVIEW: "Aksiyon onizlemesi",
            PanelItemType.CONFIRMATION_REQUIRED: "Onay bekleyen aksiyon",
            PanelItemType.CLARIFICATION_REQUIRED: "Ek bilgi gerekli",
            PanelItemType.BLOCKED: "Engellenen aksiyon",
        }[item_type]
        if assistant_metadata.get("panel_title"):
            title = assistant_metadata["panel_title"]

        summary = sanitize_text(assistant_metadata.get("panel_summary", response.assistant_message))
        blocked_reason = sanitize_text(response.permission_decision.reason) if response.blocked and response.permission_decision else ""
        confirmation_prompt = sanitize_text(response.permission_decision.confirmation_prompt) if response.permission_decision else ""
        if item_type is PanelItemType.BLOCKED:
            if not summary or summary == "[redacted-sensitive-text]":
                summary = "Bu istek guvenlik politikasi nedeniyle engellendi."
            if not blocked_reason or blocked_reason == "[redacted-sensitive-text]":
                blocked_reason = "Guvenlik politikasi bu aksiyonu engelliyor."
            if not confirmation_prompt or confirmation_prompt == "[redacted-sensitive-text]":
                confirmation_prompt = "Bu islem engelli oldugu icin approve edilemez."

        home_plan = None
        if action_type.startswith("device."):
            home_plan, _ = self.home_service.preview_plan(response.user_message, source=ActionSource(source))
            home_plan = _to_dict(home_plan)

        return PermissionPanelItem(
            item_id=f"panel-{uuid4().hex[:12]}",
            item_type=item_type,
            status=status,
            title=title,
            summary=summary,
            user_message=sanitize_text(response.user_message),
            action_type=action_type,
            target=sanitize_text(target),
            risk_level=risk_level,
            source=source,
            requires_confirmation=response.confirmation_required,
            confirmation_prompt=confirmation_prompt,
            warnings=[sanitize_text(item) for item in response.warnings],
            blocked_reason=blocked_reason,
            clarification_prompt=sanitize_text(response.assistant_message) if response.clarification_required else "",
            preview_payload={
                "assistant_message": sanitize_text(response.assistant_message),
                "response_type": response.response_type.value,
                "personal_assistant": sanitize_value(assistant_metadata),
            },
            permission_decision=permission_decision,
            pc_plan=_to_dict(response.pc_plan),
            home_plan=home_plan,
            expires_at=default_expiry(),
            audit_metadata=sanitize_value(response.audit_metadata),
            metadata=sanitize_value(response.metadata),
        )

    def create_from_home_plan(self, home_plan, *, user_message: str = "") -> PermissionPanelItem:
        return PermissionPanelItem(
            item_id=f"panel-{uuid4().hex[:12]}",
            item_type=PanelItemType.CONFIRMATION_REQUIRED if home_plan.requires_confirmation else PanelItemType.ACTION_PREVIEW,
            status=PanelItemStatus.PENDING,
            title="Home preview",
            summary=sanitize_text(home_plan.summary),
            user_message=sanitize_text(user_message),
            action_type=home_plan.action_type,
            target=sanitize_text(home_plan.device_id),
            risk_level=getattr(home_plan.risk_level, "value", str(home_plan.risk_level)),
            source="text",
            requires_confirmation=home_plan.requires_confirmation,
            warnings=[sanitize_text(item) for item in home_plan.warnings],
            blocked_reason=sanitize_text(home_plan.blocked_reason),
            preview_payload={"summary": sanitize_text(home_plan.summary)},
            home_plan=_to_dict(home_plan),
            expires_at=default_expiry(),
            audit_metadata=sanitize_value(home_plan.audit_metadata),
        )

    def create_from_pc_plan(self, pc_plan, *, user_message: str = "") -> PermissionPanelItem:
        return PermissionPanelItem(
            item_id=f"panel-{uuid4().hex[:12]}",
            item_type=PanelItemType.CONFIRMATION_REQUIRED if pc_plan.requires_confirmation else PanelItemType.ACTION_PREVIEW,
            status=PanelItemStatus.PENDING,
            title="PC preview",
            summary=sanitize_text(pc_plan.summary),
            user_message=sanitize_text(user_message),
            action_type=pc_plan.action_type,
            target=sanitize_text(pc_plan.resolved_target or pc_plan.target),
            risk_level=getattr(pc_plan.risk_level, "value", str(pc_plan.risk_level)),
            source="text",
            requires_confirmation=pc_plan.requires_confirmation,
            blocked_reason=sanitize_text(pc_plan.blocked_reason),
            preview_payload={"summary": sanitize_text(pc_plan.summary)},
            pc_plan=_to_dict(pc_plan),
            expires_at=default_expiry(),
            audit_metadata=sanitize_value(pc_plan.audit_metadata),
        )

    def create_from_routine_preview(self, routine_preview, *, user_message: str = "") -> PermissionPanelItem:
        return PermissionPanelItem(
            item_id=f"panel-{uuid4().hex[:12]}",
            item_type=PanelItemType.CONFIRMATION_REQUIRED if routine_preview.requires_confirmation else PanelItemType.ACTION_PREVIEW,
            status=PanelItemStatus.PENDING,
            title="Routine preview",
            summary=sanitize_text(routine_preview.summary),
            user_message=sanitize_text(user_message),
            action_type="routine.preview",
            target=sanitize_text(routine_preview.routine_name),
            risk_level=str(routine_preview.risk_level),
            source="routine",
            requires_confirmation=routine_preview.requires_confirmation,
            blocked_reason=sanitize_text(routine_preview.blocked_reason or ""),
            warnings=[sanitize_text(item) for item in routine_preview.warnings],
            routine_preview=_to_dict(routine_preview),
            expires_at=default_expiry(),
            audit_metadata=sanitize_value(routine_preview.audit_metadata),
        )

    def submit_text(self, text: str, source: ActionSource = ActionSource.TEXT, project_name: str = "ATLAS") -> PanelOperationResult:
        response = self.loop.handle_text(message=text, project_name=project_name, source=source)
        item = self.create_from_conversation(response)
        if item is None:
            return PanelOperationResult(
                status=PanelOperationStatus.SKIPPED,
                message="Bu cevap panel kuyruuna alinmadi.",
                metadata={"response_type": response.response_type.value},
            )
        self.store.add(item)
        return PanelOperationResult(
            status=PanelOperationStatus.CREATED,
            message="Panel ogesi olusturuldu. Bu sadece onizlemedir, islem calistirilmadi.",
            item=item,
            metadata={"response_type": response.response_type.value},
        )

    def list_items(self, status: str | None = None) -> PanelOperationResult:
        items = self.store.list(status=status)
        return PanelOperationResult(
            status=PanelOperationStatus.LISTED,
            message=f"{len(items)} panel ogesi listelendi.",
            items=items,
            metadata=self._state_metadata(items),
        )

    def show_item(self, item_id: str) -> PanelOperationResult:
        item = self.store.get(item_id)
        if item is None:
            return PanelOperationResult(status=PanelOperationStatus.NOT_FOUND, message="Panel ogesi bulunamadi.")
        return PanelOperationResult(status=PanelOperationStatus.SHOWN, message="Panel ogesi gosterildi.", item=item)

    def approve_item(self, item_id: str, reason: str | None = None) -> PanelOperationResult:
        item = self.store.get(item_id)
        if item is None:
            return PanelOperationResult(status=PanelOperationStatus.NOT_FOUND, message="Panel ogesi bulunamadi.")
        allowed, blocked_reason = can_approve(item)
        if not allowed:
            return PanelOperationResult(status=PanelOperationStatus.BLOCKED, message=blocked_reason, item=item)
        decision = PanelDecision(
            decision_id=f"decision-{uuid4().hex[:12]}",
            item_id=item.item_id,
            decision=PanelDecisionType.APPROVE,
            reason=sanitize_text(reason or ""),
            user_confirmed=True,
            execution_allowed=False,
            execution_attempted=False,
            metadata={"ready_for_future_execution": True},
        )
        item.item_type = PanelItemType.APPROVED_PREVIEW
        updated = self.store.approve(item_id, decision)
        return PanelOperationResult(
            status=PanelOperationStatus.APPROVED,
            message="Panel ogesi approved_preview durumuna alindi. Gercek execution baslatilmadi.",
            item=updated,
            decision=decision,
        )

    def deny_item(self, item_id: str, reason: str | None = None) -> PanelOperationResult:
        item = self.store.get(item_id)
        if item is None:
            return PanelOperationResult(status=PanelOperationStatus.NOT_FOUND, message="Panel ogesi bulunamadi.")
        decision = PanelDecision(
            decision_id=f"decision-{uuid4().hex[:12]}",
            item_id=item.item_id,
            decision=PanelDecisionType.DENY,
            reason=sanitize_text(reason or ""),
            user_confirmed=False,
            execution_allowed=False,
            execution_attempted=False,
        )
        item.item_type = PanelItemType.DENIED
        updated = self.store.deny(item_id, decision)
        return PanelOperationResult(
            status=PanelOperationStatus.DENIED,
            message="Panel ogesi deny durumuna alindi. Gercek execution yok.",
            item=updated,
            decision=decision,
        )

    def cancel_item(self, item_id: str, reason: str | None = None) -> PanelOperationResult:
        item = self.store.get(item_id)
        if item is None:
            return PanelOperationResult(status=PanelOperationStatus.NOT_FOUND, message="Panel ogesi bulunamadi.")
        decision = PanelDecision(
            decision_id=f"decision-{uuid4().hex[:12]}",
            item_id=item.item_id,
            decision=PanelDecisionType.CANCEL,
            reason=sanitize_text(reason or ""),
            user_confirmed=False,
            execution_allowed=False,
            execution_attempted=False,
        )
        item.item_type = PanelItemType.CANCELLED
        updated = self.store.cancel(item_id, decision)
        return PanelOperationResult(
            status=PanelOperationStatus.CANCELLED,
            message="Panel ogesi iptal edildi. Gercek execution yok.",
            item=updated,
            decision=decision,
        )

    def clear_items(self) -> PanelOperationResult:
        count = self.store.clear()
        return PanelOperationResult(
            status=PanelOperationStatus.LISTED,
            message=f"{count} panel ogesi temizlendi.",
            metadata={"cleared_count": count},
        )

    def state(self) -> PermissionPanelState:
        items = self.store.list()
        return PermissionPanelState(
            pending_count=sum(1 for item in items if item.status is PanelItemStatus.PENDING),
            blocked_count=sum(1 for item in items if item.status is PanelItemStatus.BLOCKED),
            approved_count=sum(1 for item in items if item.status is PanelItemStatus.APPROVED),
            denied_count=sum(1 for item in items if item.status is PanelItemStatus.DENIED),
            cancelled_count=sum(1 for item in items if item.status is PanelItemStatus.CANCELLED),
            items=items,
            metadata={"execution_attempted": False},
        )

    def _state_metadata(self, items: list[PermissionPanelItem]) -> dict[str, int]:
        return {
            "pending_count": sum(1 for item in items if item.status is PanelItemStatus.PENDING),
            "blocked_count": sum(1 for item in items if item.status is PanelItemStatus.BLOCKED),
            "approved_count": sum(1 for item in items if item.status is PanelItemStatus.APPROVED),
            "denied_count": sum(1 for item in items if item.status is PanelItemStatus.DENIED),
            "cancelled_count": sum(1 for item in items if item.status is PanelItemStatus.CANCELLED),
        }
