from app.personal_assistant.calendar import CalendarService
from app.personal_assistant.models import CalendarOperation, CalendarStatus, ReminderSource
from app.personal_assistant.store import InMemoryAssistantStore


def build_service() -> CalendarService:
    return CalendarService(store=InMemoryAssistantStore())


def test_query_calendar_local_only_response() -> None:
    service = build_service()
    result = service.query_calendar("Bugun takvimimde ne var?", source=ReminderSource.TEXT)
    assert result.status is CalendarStatus.SAFE_QUERY_PREVIEW
    assert result.operation is CalendarOperation.QUERY
    assert result.audit_metadata["external_calendar_used"] is False


def test_create_event_draft_pending_confirmation() -> None:
    service = build_service()
    result = service.create_event_draft("Yarin 10a toplanti ekle", source=ReminderSource.TEXT)
    assert result.status is CalendarStatus.PENDING_CONFIRMATION
    assert result.event_draft is not None
    assert result.event_draft.status is CalendarStatus.PENDING_CONFIRMATION
    assert result.audit_metadata["execution_attempted"] is False


def test_list_and_cancel_event_draft() -> None:
    service = build_service()
    created = service.create_event_draft("Cuma 1400e gorusme koy", source=ReminderSource.TEXT)
    listed = service.list_event_drafts()
    assert listed.status is CalendarStatus.LISTED
    assert len(listed.event_drafts) == 1

    cancelled = service.cancel_event_draft(created.event_draft.event_id)
    assert cancelled.status is CalendarStatus.CANCELLED
