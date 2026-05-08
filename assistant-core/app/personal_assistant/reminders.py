from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.personal_assistant.models import (
    NotificationChannel,
    ReminderDefinition,
    ReminderOperation,
    ReminderOperationResult,
    ReminderResultStatus,
    ReminderSource,
    ReminderStatus,
)
from app.personal_assistant.notifications import NotificationService
from app.personal_assistant.parser import parse_datetime_text, parse_reminder_request
from app.personal_assistant.policy import PersonalAssistantPolicy
from app.personal_assistant.store import InMemoryAssistantStore, get_store


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ReminderService:
    def __init__(
        self,
        *,
        store: InMemoryAssistantStore | None = None,
        policy: PersonalAssistantPolicy | None = None,
        notification_service: NotificationService | None = None,
    ) -> None:
        self.store = store or get_store()
        self.policy = policy or PersonalAssistantPolicy()
        self.notification_service = notification_service or NotificationService(policy=self.policy)

    def create_reminder(self, text: str, source: ReminderSource = ReminderSource.TEXT) -> ReminderOperationResult:
        operation, payload = parse_reminder_request(text)
        if operation is not ReminderOperation.CREATE:
            return ReminderOperationResult(
                status=ReminderResultStatus.INVALID,
                operation=ReminderOperation.CREATE,
                message="Hatırlatıcı isteği anlaşılamadı. Gerçek işlem yapılmadı.",
                audit_metadata={"execution_attempted": False},
            )

        reminder_text = str(payload.get("reminder_text", "")).strip()
        due_at_text = str(payload.get("due_at_text", "")).strip()
        blocked, warnings, blocked_reason = self.policy.inspect_text(reminder_text)
        if blocked:
            return ReminderOperationResult(
                status=ReminderResultStatus.BLOCKED,
                operation=ReminderOperation.CREATE,
                message="Hatırlatıcı isteği güvenlik nedeniyle engellendi. Gerçek işlem yapılmadı.",
                warnings=warnings,
                blocked_reason=blocked_reason,
                audit_metadata={
                    "execution_attempted": False,
                    "permission_status": "blocked",
                    "scheduler_enabled": False,
                    "os_notification_sent": False,
                },
            )

        reminder = ReminderDefinition(
            reminder_id=f"reminder-{uuid4().hex[:12]}",
            title=_title_from_text(reminder_text),
            message=reminder_text,
            due_at_text=due_at_text,
            due_at=parse_datetime_text(due_at_text),
            source=source,
            status=ReminderStatus.PENDING_CONFIRMATION,
            requires_confirmation=True,
            metadata={
                "local_only": True,
                "scheduler_enabled": False,
                "os_notification_sent": False,
                "execution_attempted": False,
            },
        )
        decision = self.policy.reminder_create_decision(reminder, source=source, raw_text=text)
        reminder.metadata["permission_status"] = decision.status.value
        reminder.metadata["permission_decision"] = {
            "status": decision.status.value,
            "reason": decision.reason,
            "confirmation_prompt": decision.confirmation_prompt,
        }
        self.store.add_reminder(reminder)

        notification_result = self.notification_service.build_notification_preview(
            title="Hatırlatıcı taslağı önizlemesi",
            body=f"{reminder.title} - {due_at_text or 'zaman bilgisi belirsiz'}",
            channel=NotificationChannel.CLI,
            source=source,
        )
        audit_metadata = dict(decision.audit_metadata)
        audit_metadata.update(
            {
                "scheduler_enabled": False,
                "os_notification_sent": False,
                "notification_preview_status": notification_result.status.value,
                "execution_attempted": False,
            }
        )
        return ReminderOperationResult(
            status=ReminderResultStatus.PENDING_CONFIRMATION,
            operation=ReminderOperation.CREATE,
            reminder=reminder,
            message=(
                "Hatırlatıcı taslağı local önizleme olarak kaydedildi. "
                "Onay gerekiyor. Gerçek scheduler veya OS notification çalıştırılmadı."
            ),
            warnings=warnings + notification_result.warnings,
            audit_metadata=audit_metadata,
        )

    def list_reminders(self) -> ReminderOperationResult:
        reminders = self.store.list_reminders()
        message = "Kayitli hatirlatici yok." if not reminders else f"{len(reminders)} local hatirlatici taslagi listelendi."
        return ReminderOperationResult(
            status=ReminderResultStatus.LISTED,
            operation=ReminderOperation.LIST,
            reminders=reminders,
            message=message,
            audit_metadata={"execution_attempted": False, "count": len(reminders)},
        )

    def cancel_reminder(self, identifier: str) -> ReminderOperationResult:
        reminder = _find_reminder(self.store.list_reminders(), identifier)
        if reminder is None:
            return ReminderOperationResult(
                status=ReminderResultStatus.NOT_FOUND,
                operation=ReminderOperation.CANCEL,
                message="Hatırlatıcı taslağı bulunamadı. Gerçek işlem yapılmadı.",
                audit_metadata={"execution_attempted": False},
            )

        cancelled = self.store.cancel_reminder(reminder.reminder_id)
        return ReminderOperationResult(
            status=ReminderResultStatus.CANCELLED,
            operation=ReminderOperation.CANCEL,
            reminder=cancelled,
            message="Hatırlatıcı taslağı local kayıttan iptal edildi. Gerçek scheduler yoktu.",
            audit_metadata={
                "execution_attempted": False,
                "scheduler_enabled": False,
                "cancelled_reminder_id": reminder.reminder_id,
            },
        )

    def preview_reminder(self, text: str) -> ReminderOperationResult:
        operation, payload = parse_reminder_request(text)
        if operation is not ReminderOperation.CREATE:
            return ReminderOperationResult(
                status=ReminderResultStatus.INVALID,
                operation=ReminderOperation.PREVIEW,
                message="Hatırlatıcı önizlemesi için create benzeri bir metin gerekli. Gerçek işlem yapılmadı.",
                audit_metadata={"execution_attempted": False},
            )
        reminder_text = str(payload.get("reminder_text", "")).strip()
        due_at_text = str(payload.get("due_at_text", "")).strip()
        reminder = ReminderDefinition(
            reminder_id="preview-reminder",
            title=_title_from_text(reminder_text),
            message=reminder_text,
            due_at_text=due_at_text,
            due_at=parse_datetime_text(due_at_text),
            source=ReminderSource.TEXT,
            status=ReminderStatus.SCHEDULED_PREVIEW,
            requires_confirmation=True,
            metadata={
                "local_only": True,
                "scheduler_enabled": False,
                "execution_attempted": False,
            },
        )
        return ReminderOperationResult(
            status=ReminderResultStatus.PREVIEW,
            operation=ReminderOperation.PREVIEW,
            reminder=reminder,
            message="Hatırlatıcı taslağı önizlemesi hazırlandı. Gerçek alarm kurulmadı.",
            audit_metadata={"execution_attempted": False, "scheduler_enabled": False},
        )

    def format_result(self, result: ReminderOperationResult) -> str:
        if result.status is ReminderResultStatus.LISTED:
            if not result.reminders:
                return result.message
            lines = ["Hatırlatıcı taslakları:"]
            for reminder in result.reminders:
                due_text = reminder.due_at_text or "zaman yok"
                lines.append(
                    f"- {reminder.reminder_id} | {reminder.status.value} | {reminder.title} | {due_text}"
                )
            lines.append("Not: Bu liste yalnızca local önizleme taslaklarını gösterir; gerçek scheduler veya OS notification yok.")
            return "\n".join(lines)
        if result.reminder is not None:
            due_text = result.reminder.due_at_text or "zaman bilgisi belirsiz"
            return f"{result.message}\nID: {result.reminder.reminder_id}\nBaslik: {result.reminder.title}\nZaman: {due_text}"
        return result.message


def _title_from_text(text: str) -> str:
    value = " ".join(text.split()).strip()
    return value[:80] if value else "Hatirlatici"


def _find_reminder(reminders: list[ReminderDefinition], identifier: str) -> ReminderDefinition | None:
    normalized = identifier.strip().lower()
    if normalized == "last":
        return reminders[0] if reminders else None
    for reminder in reminders:
        if reminder.reminder_id == identifier or reminder.reminder_id.startswith(identifier):
            return reminder
    for reminder in reminders:
        if normalized in reminder.title.lower() or normalized in reminder.message.lower():
            return reminder
    return None
