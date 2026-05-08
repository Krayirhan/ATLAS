from app.personal_assistant.models import (
    CalendarEventDraft,
    NotificationChannel,
    NotificationDraft,
    ReminderDefinition,
    ReminderOperation,
    ReminderSource,
    ReminderStatus,
)
from app.personal_assistant.parser import parse_calendar_request, parse_reminder_request
from app.personal_assistant.policy import PersonalAssistantPolicy


def test_reminder_definition_can_be_created() -> None:
    reminder = ReminderDefinition(
        reminder_id="reminder-1",
        title="Su ic",
        message="Su icmeyi hatirlat",
        due_at_text="20 dakika sonra",
        source=ReminderSource.TEXT,
        status=ReminderStatus.PENDING_CONFIRMATION,
    )
    assert reminder.title == "Su ic"
    assert reminder.status is ReminderStatus.PENDING_CONFIRMATION


def test_calendar_event_draft_can_be_created() -> None:
    draft = CalendarEventDraft(
        event_id="event-1",
        title="Toplanti",
        start_text="yarin 10a",
        source=ReminderSource.TEXT,
    )
    assert draft.title == "Toplanti"
    assert draft.requires_confirmation is True


def test_notification_draft_can_be_created() -> None:
    notification = NotificationDraft(
        notification_id="notification-1",
        title="Hatirlatma",
        body="Su ic",
        channel=NotificationChannel.CLI,
        source=ReminderSource.TEXT,
    )
    assert notification.channel is NotificationChannel.CLI
    assert notification.body == "Su ic"


def test_parser_matches_reminder_create_and_list() -> None:
    operation, payload = parse_reminder_request("Bana 20 dakika sonra su icmeyi hatirlat")
    assert operation is ReminderOperation.CREATE
    assert payload["due_at_text"] == "20 dakika sonra"

    list_operation, _ = parse_reminder_request("Hatirlaticilarimi goster")
    assert list_operation is ReminderOperation.LIST


def test_parser_matches_calendar_query_and_event_draft() -> None:
    query_operation, query_payload = parse_calendar_request("Bugun takvimimde ne var?")
    assert query_operation.value == "query"
    assert query_payload["date_text"] == "bugun"

    draft_operation, draft_payload = parse_calendar_request("Yarin 10a toplanti ekle")
    assert draft_operation.value == "draft_event"
    assert draft_payload["title"] == "toplanti"


def test_policy_blocks_sensitive_reminder_text() -> None:
    blocked, warnings, blocked_reason = PersonalAssistantPolicy().inspect_text("Sifremi yarin hatirlat")
    assert blocked is True
    assert warnings == []
    assert blocked_reason is not None
