from __future__ import annotations

from uuid import uuid4

from app.actions.models import ActionCandidate, PermissionDecision
from app.actions.permission import PermissionManager
from app.actions.risk import RiskLevel
from app.actions.types import ActionSource, ActionType, IntentCategory
from app.personal_assistant.models import (
    CalendarEventDraft,
    CalendarQuery,
    NotificationChannel,
    ReminderDefinition,
    ReminderSource,
)
from app.personal_assistant.parser import normalize_text


POLICY_VERSION = "personal-assistant-v1"
BLOCKED_KEYWORDS = (
    "sifre",
    "password",
    "token",
    "api key",
    "secret",
    "credential",
    "tc kimlik",
    "kimlik no",
    "kredi karti",
    "iban",
    "cvv",
    "seed phrase",
    "recovery code",
)
SENSITIVE_WARNING_KEYWORDS = {
    "medical": ("ilac", "doz", "recete", "insulin"),
    "financial": ("fatura", "odeme", "vergi", "kredi"),
    "identity": ("pasaport", "ehliyet", "kimlik", "oturum karti"),
}


class PersonalAssistantPolicy:
    def __init__(self, permission_manager: PermissionManager | None = None) -> None:
        self.permission_manager = permission_manager or PermissionManager()

    def inspect_text(self, text: str) -> tuple[bool, list[str], str | None]:
        normalized = normalize_text(text)
        if any(token in normalized for token in BLOCKED_KEYWORDS):
            return True, [], "Bu icerik credential, kimlik veya finansal gizli veri benzeri oldugu icin blocked."

        warnings: list[str] = []
        for label, tokens in SENSITIVE_WARNING_KEYWORDS.items():
            if any(token in normalized for token in tokens):
                warnings.append(f"{label} hassasligi nedeniyle bu icerik local preview sinirinda tutuluyor.")
        return False, warnings, None

    def reminder_create_decision(self, reminder: ReminderDefinition, *, source: ReminderSource, raw_text: str) -> PermissionDecision:
        return self.permission_manager.decide(
            self._candidate(
                action_type=ActionType.REMINDER_CREATE,
                intent_category=IntentCategory.REMINDER_CREATE,
                target=reminder.title,
                parameters={
                    "due_at_text": reminder.due_at_text,
                    "recurrence": reminder.recurrence,
                    "reminder_id": reminder.reminder_id,
                },
                source=source,
                user_goal=raw_text,
                expected_result="Local reminder preview kaydi olusturulur; gercek scheduler veya OS notification yok.",
            )
        )

    def calendar_query_decision(self, query: CalendarQuery, *, source: ReminderSource, raw_text: str) -> PermissionDecision:
        return self.permission_manager.decide(
            self._candidate(
                action_type=ActionType.CALENDAR_QUERY,
                intent_category=IntentCategory.CALENDAR_QUERY,
                target=query.date_text or "local_calendar_preview",
                parameters={"query_id": query.query_id, "date_text": query.date_text},
                source=source,
                user_goal=raw_text,
                expected_result="Local calendar draft gorunumu preview edilir; external calendar okunmaz.",
            )
        )

    def calendar_event_decision(self, event: CalendarEventDraft, *, source: ReminderSource, raw_text: str) -> PermissionDecision:
        return self.permission_manager.decide(
            self._candidate(
                action_type=ActionType.CALENDAR_EVENT_DRAFT,
                intent_category=IntentCategory.CALENDAR_EVENT_DRAFT,
                target=event.title,
                parameters={
                    "event_id": event.event_id,
                    "start_text": event.start_text,
                    "end_text": event.end_text,
                },
                source=source,
                user_goal=raw_text,
                expected_result="Calendar event draft local preview olarak kaydedilir; external write yok.",
            )
        )

    def notification_allowed(self, title: str, body: str, *, channel: NotificationChannel) -> tuple[bool, list[str], str | None]:
        blocked, warnings, blocked_reason = self.inspect_text(f"{title} {body}")
        if blocked:
            return False, warnings, blocked_reason
        if channel is not NotificationChannel.CLI:
            warnings.append("Bu kanal future-only durumunda; yalnizca preview metni uretildi.")
        return True, warnings, None

    def _candidate(
        self,
        *,
        action_type: ActionType,
        intent_category: IntentCategory,
        target: str,
        parameters: dict[str, object],
        source: ReminderSource,
        user_goal: str,
        expected_result: str,
    ) -> ActionCandidate:
        action_source = _action_source_from_reminder_source(source)
        risk_level = {
            ActionType.CALENDAR_QUERY: RiskLevel.SAFE_READONLY,
            ActionType.REMINDER_CREATE: RiskLevel.MEDIUM,
            ActionType.CALENDAR_EVENT_DRAFT: RiskLevel.MEDIUM,
        }.get(action_type, RiskLevel.MEDIUM)
        return ActionCandidate(
            action_id=f"action-{uuid4().hex[:12]}",
            action_type=action_type,
            target=target,
            parameters=parameters,
            source=action_source,
            user_goal=user_goal,
            intent_category=intent_category,
            risk_level=risk_level,
            requires_confirmation=risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH},
            dry_run_supported=True,
            reversible=True,
            expected_result=expected_result,
            audit_metadata={
                "policy_version": POLICY_VERSION,
                "execution_attempted": False,
            },
        )


def _action_source_from_reminder_source(source: ReminderSource) -> ActionSource:
    mapping = {
        ReminderSource.TEXT: ActionSource.TEXT,
        ReminderSource.VOICE: ActionSource.VOICE,
        ReminderSource.ROUTINE: ActionSource.ROUTINE,
        ReminderSource.SCHEDULE: ActionSource.SCHEDULE,
        ReminderSource.MANUAL: ActionSource.MANUAL,
    }
    return mapping.get(source, ActionSource.UNKNOWN)
