from app.personal_assistant.models import ReminderResultStatus, ReminderSource, ReminderStatus
from app.personal_assistant.reminders import ReminderService
from app.personal_assistant.store import InMemoryAssistantStore


def build_service() -> ReminderService:
    return ReminderService(store=InMemoryAssistantStore())


def test_create_reminder_pending_confirmation() -> None:
    service = build_service()
    result = service.create_reminder("Bana 20 dakika sonra su icmeyi hatirlat", source=ReminderSource.TEXT)
    assert result.status is ReminderResultStatus.PENDING_CONFIRMATION
    assert result.reminder is not None
    assert result.reminder.status is ReminderStatus.PENDING_CONFIRMATION
    assert result.audit_metadata["execution_attempted"] is False


def test_list_reminders_works() -> None:
    service = build_service()
    service.create_reminder("Bana 20 dakika sonra su icmeyi hatirlat")
    result = service.list_reminders()
    assert result.status is ReminderResultStatus.LISTED
    assert len(result.reminders) == 1


def test_cancel_reminder_works() -> None:
    service = build_service()
    created = service.create_reminder("Bana 20 dakika sonra su icmeyi hatirlat")
    cancelled = service.cancel_reminder(created.reminder.reminder_id)
    assert cancelled.status is ReminderResultStatus.CANCELLED
    assert cancelled.reminder.status is ReminderStatus.CANCELLED


def test_sensitive_reminder_is_blocked() -> None:
    service = build_service()
    result = service.create_reminder("Bana sifremi yarin hatirlat")
    assert result.status is ReminderResultStatus.BLOCKED
    assert result.blocked_reason is not None
