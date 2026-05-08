from __future__ import annotations

from app.actions.types import ActionSource
from app.personal_assistant.calendar import CalendarService
from app.personal_assistant.models import CalendarOperation, ReminderOperation, ReminderSource
from app.personal_assistant.notifications import NotificationService
from app.personal_assistant.parser import parse_calendar_request, parse_reminder_request
from app.personal_assistant.policy import PersonalAssistantPolicy
from app.personal_assistant.reminders import ReminderService
from app.personal_assistant.store import InMemoryAssistantStore, get_store


class PersonalAssistantService:
    def __init__(self, *, store: InMemoryAssistantStore | None = None) -> None:
        shared_store = store or get_store()
        policy = PersonalAssistantPolicy()
        self.reminder_service = ReminderService(store=shared_store, policy=policy)
        self.calendar_service = CalendarService(store=shared_store, policy=policy)
        self.notification_service = NotificationService(policy=policy)

    def handle_text(self, text: str, source: ActionSource = ActionSource.TEXT):
        reminder_operation, reminder_payload = parse_reminder_request(text)
        reminder_source = _reminder_source(source)
        if reminder_operation is ReminderOperation.CREATE:
            return self.reminder_service.create_reminder(text, source=reminder_source)
        if reminder_operation is ReminderOperation.LIST:
            return self.reminder_service.list_reminders()
        if reminder_operation is ReminderOperation.CANCEL:
            return self.reminder_service.cancel_reminder(str(reminder_payload.get("identifier", "last")))

        calendar_operation, calendar_payload = parse_calendar_request(text)
        if calendar_operation is CalendarOperation.QUERY:
            return self.calendar_service.query_calendar(text, source=reminder_source)
        if calendar_operation is CalendarOperation.DRAFT_EVENT:
            return self.calendar_service.create_event_draft(text, source=reminder_source)
        if calendar_operation is CalendarOperation.LIST_LOCAL:
            return self.calendar_service.list_event_drafts()
        if calendar_operation is CalendarOperation.CANCEL_DRAFT:
            return self.calendar_service.cancel_event_draft(str(calendar_payload.get("identifier", "last")))

        return None


def _reminder_source(source: ActionSource) -> ReminderSource:
    mapping = {
        ActionSource.TEXT: ReminderSource.TEXT,
        ActionSource.VOICE: ReminderSource.VOICE,
        ActionSource.ROUTINE: ReminderSource.ROUTINE,
        ActionSource.SCHEDULE: ReminderSource.SCHEDULE,
        ActionSource.MANUAL: ReminderSource.MANUAL,
    }
    return mapping.get(source, ReminderSource.UNKNOWN)
