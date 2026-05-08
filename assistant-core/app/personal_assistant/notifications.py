from __future__ import annotations

from uuid import uuid4

from app.personal_assistant.models import (
    NotificationChannel,
    NotificationDraft,
    NotificationOperationResult,
    NotificationStatus,
    ReminderSource,
)
from app.personal_assistant.policy import PersonalAssistantPolicy


class NotificationService:
    def __init__(self, policy: PersonalAssistantPolicy | None = None) -> None:
        self.policy = policy or PersonalAssistantPolicy()

    def build_notification_preview(
        self,
        title: str,
        body: str,
        channel: NotificationChannel = NotificationChannel.CLI,
        source: ReminderSource = ReminderSource.TEXT,
    ) -> NotificationOperationResult:
        allowed, warnings, blocked_reason = self.policy.notification_allowed(title, body, channel=channel)
        if not allowed:
            return NotificationOperationResult(
                status=NotificationStatus.BLOCKED,
                message="Notification preview blocked.",
                warnings=warnings,
                audit_metadata={
                    "blocked_reason": blocked_reason,
                    "execution_attempted": False,
                    "os_notification_sent": False,
                },
            )

        notification = NotificationDraft(
            notification_id=f"notification-{uuid4().hex[:12]}",
            title=title,
            body=body,
            channel=channel,
            source=source,
            metadata={
                "delivery_mode": "preview_only",
                "os_notification_sent": False,
            },
        )
        return NotificationOperationResult(
            status=NotificationStatus.PREVIEW,
            notification=notification,
            message="Notification preview hazirlandi. Gercek OS notification yok.",
            warnings=warnings,
            audit_metadata={
                "execution_attempted": False,
                "os_notification_sent": False,
                "channel": channel.value,
            },
        )

    def format_notification(self, notification: NotificationDraft) -> str:
        return f"[{notification.channel.value}] {notification.title}: {notification.body}"
