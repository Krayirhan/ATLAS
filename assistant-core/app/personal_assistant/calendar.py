from __future__ import annotations

from uuid import uuid4

from app.personal_assistant.models import (
    CalendarEventDraft,
    CalendarOperation,
    CalendarOperationResult,
    CalendarQuery,
    CalendarStatus,
    ReminderSource,
)
from app.personal_assistant.parser import parse_calendar_range, parse_calendar_request, parse_datetime_text
from app.personal_assistant.policy import PersonalAssistantPolicy
from app.personal_assistant.store import InMemoryAssistantStore, get_store


class CalendarService:
    def __init__(self, *, store: InMemoryAssistantStore | None = None, policy: PersonalAssistantPolicy | None = None) -> None:
        self.store = store or get_store()
        self.policy = policy or PersonalAssistantPolicy()

    def query_calendar(self, text: str, source: ReminderSource = ReminderSource.TEXT) -> CalendarOperationResult:
        operation, payload = parse_calendar_request(text)
        if operation is not CalendarOperation.QUERY:
            return CalendarOperationResult(
                status=CalendarStatus.UNSUPPORTED,
                operation=CalendarOperation.QUERY,
                message="Calendar query anlasilamadi.",
                audit_metadata={"execution_attempted": False, "external_calendar_used": False},
            )

        date_text = str(payload.get("date_text", "")).strip() or "bugun"
        range_start, range_end = parse_calendar_range(date_text)
        query = CalendarQuery(
            query_id=f"calendar-query-{uuid4().hex[:12]}",
            query_text=text,
            date_text=date_text,
            range_start=range_start,
            range_end=range_end,
            source=source,
            metadata={
                "local_only": True,
                "external_calendar_used": False,
            },
        )
        decision = self.policy.calendar_query_decision(query, source=source, raw_text=text)
        drafts = _filter_drafts(self.store.list_calendar_drafts(), range_start, range_end)
        message = (
            "Local takvim preview sonucu hazir. "
            "Harici calendar entegrasyonu kapali; yalnizca local draftlar gosterildi."
        )
        if drafts:
            message += f" {len(drafts)} local draft eslesti."
        else:
            message += " Eslesen local draft yok."
        return CalendarOperationResult(
            status=CalendarStatus.SAFE_QUERY_PREVIEW,
            operation=CalendarOperation.QUERY,
            query=query,
            event_drafts=drafts,
            message=message,
            warnings=list(decision.warnings),
            audit_metadata={
                **decision.audit_metadata,
                "external_calendar_used": False,
                "execution_attempted": False,
            },
        )

    def create_event_draft(self, text: str, source: ReminderSource = ReminderSource.TEXT) -> CalendarOperationResult:
        operation, payload = parse_calendar_request(text)
        if operation is not CalendarOperation.DRAFT_EVENT:
            return CalendarOperationResult(
                status=CalendarStatus.UNSUPPORTED,
                operation=CalendarOperation.DRAFT_EVENT,
                message="Calendar draft istegi anlasilamadi.",
                audit_metadata={"execution_attempted": False, "external_calendar_used": False},
            )

        title = str(payload.get("title", "")).strip()
        start_text = str(payload.get("start_text", "")).strip()
        blocked, warnings, blocked_reason = self.policy.inspect_text(title)
        if blocked:
            return CalendarOperationResult(
                status=CalendarStatus.BLOCKED,
                operation=CalendarOperation.DRAFT_EVENT,
                message="Calendar draft istegi guvenlik nedeniyle blocked.",
                warnings=warnings,
                blocked_reason=blocked_reason,
                audit_metadata={"execution_attempted": False, "external_calendar_used": False},
            )

        draft = CalendarEventDraft(
            event_id=f"event-{uuid4().hex[:12]}",
            title=title[:120] or "Takvim Etkinligi",
            start_text=start_text,
            start_at=parse_datetime_text(start_text),
            source=source,
            requires_confirmation=True,
            status=CalendarStatus.PENDING_CONFIRMATION,
            metadata={
                "local_only": True,
                "external_calendar_used": False,
                "execution_attempted": False,
            },
        )
        decision = self.policy.calendar_event_decision(draft, source=source, raw_text=text)
        draft.metadata["permission_status"] = decision.status.value
        self.store.add_calendar_draft(draft)
        return CalendarOperationResult(
            status=CalendarStatus.PENDING_CONFIRMATION,
            operation=CalendarOperation.DRAFT_EVENT,
            event_draft=draft,
            message=(
                "Calendar event draft local preview olarak kaydedildi ve onay bekliyor. "
                "Harici takvime yazilmadi."
            ),
            warnings=warnings + list(decision.warnings),
            audit_metadata={
                **decision.audit_metadata,
                "external_calendar_used": False,
                "execution_attempted": False,
            },
        )

    def list_event_drafts(self) -> CalendarOperationResult:
        drafts = self.store.list_calendar_drafts()
        return CalendarOperationResult(
            status=CalendarStatus.LISTED,
            operation=CalendarOperation.LIST_LOCAL,
            event_drafts=drafts,
            message="Local calendar draftlari listelendi." if drafts else "Local calendar draft yok.",
            audit_metadata={"execution_attempted": False, "external_calendar_used": False, "count": len(drafts)},
        )

    def cancel_event_draft(self, identifier: str) -> CalendarOperationResult:
        draft = _find_draft(self.store.list_calendar_drafts(), identifier)
        if draft is None:
            return CalendarOperationResult(
                status=CalendarStatus.NOT_FOUND,
                operation=CalendarOperation.CANCEL_DRAFT,
                message="Calendar draft bulunamadi.",
                audit_metadata={"execution_attempted": False, "external_calendar_used": False},
            )

        cancelled = self.store.cancel_calendar_draft(draft.event_id)
        return CalendarOperationResult(
            status=CalendarStatus.CANCELLED,
            operation=CalendarOperation.CANCEL_DRAFT,
            event_draft=cancelled,
            message="Calendar draft local kayittan iptal edildi. Harici takvim yazimi yoktu.",
            audit_metadata={
                "execution_attempted": False,
                "external_calendar_used": False,
                "event_id": draft.event_id,
            },
        )

    def format_result(self, result: CalendarOperationResult) -> str:
        if result.operation is CalendarOperation.QUERY:
            lines = [result.message]
            for draft in result.event_drafts:
                lines.append(f"- {draft.event_id} | {draft.title} | {draft.start_text or 'zaman yok'}")
            return "\n".join(lines)
        if result.operation is CalendarOperation.LIST_LOCAL:
            if not result.event_drafts:
                return result.message
            lines = ["Calendar draftlari:"]
            for draft in result.event_drafts:
                lines.append(f"- {draft.event_id} | {draft.status.value} | {draft.title} | {draft.start_text or 'zaman yok'}")
            return "\n".join(lines)
        if result.event_draft is not None:
            return (
                f"{result.message}\n"
                f"ID: {result.event_draft.event_id}\n"
                f"Baslik: {result.event_draft.title}\n"
                f"Baslangic: {result.event_draft.start_text or 'zaman yok'}"
            )
        return result.message


def _filter_drafts(
    drafts: list[CalendarEventDraft],
    range_start,
    range_end,
) -> list[CalendarEventDraft]:
    if range_start is None or range_end is None:
        return drafts
    filtered: list[CalendarEventDraft] = []
    for draft in drafts:
        if draft.start_at is None:
            continue
        if range_start <= draft.start_at <= range_end:
            filtered.append(draft)
    return filtered


def _find_draft(drafts: list[CalendarEventDraft], identifier: str) -> CalendarEventDraft | None:
    normalized = identifier.strip().lower()
    if normalized == "last":
        return drafts[0] if drafts else None
    for draft in drafts:
        if draft.event_id == identifier or draft.event_id.startswith(identifier):
            return draft
    for draft in drafts:
        if normalized in draft.title.lower():
            return draft
    return None
