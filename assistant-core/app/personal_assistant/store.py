from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from time import sleep
from typing import Any
from uuid import uuid4

from app.personal_assistant.models import CalendarEventDraft, CalendarStatus, ReminderDefinition, ReminderStatus


MAX_STORED_ITEMS = 200
MAX_STRING_LENGTH = 500
REDACTION_TOKENS = ("password", "token", "secret", "credential", "api_key")
BLOCKED_PATH_PARTS = {".env", ".pem", ".key", ".keystore", ".jks", "id_rsa", "id_ed25519"}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _default_store_path() -> Path:
    return (_repo_root() / "workspace" / "state" / "personal-assistant.json").resolve()


def _sanitize_text(value: str) -> str:
    compact = " ".join(value.strip().split())
    lowered = compact.lower()
    if any(token in lowered for token in REDACTION_TOKENS):
        return "[redacted-sensitive-text]"
    if len(compact) > MAX_STRING_LENGTH:
        return compact[:MAX_STRING_LENGTH] + "..."
    return compact


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return _sanitize_text(value)
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value[:50]]
    if isinstance(value, dict):
        safe: dict[str, Any] = {}
        for key, item in list(value.items())[:100]:
            if any(token in key.lower() for token in REDACTION_TOKENS):
                safe[key] = "[redacted]"
            else:
                safe[key] = _sanitize_value(item)
        return safe
    return value


class InMemoryAssistantStore:
    def __init__(self) -> None:
        self._reminders: dict[str, ReminderDefinition] = {}
        self._calendar_drafts: dict[str, CalendarEventDraft] = {}

    def add_reminder(self, reminder: ReminderDefinition) -> ReminderDefinition:
        self._reminders[reminder.reminder_id] = reminder
        return reminder

    def list_reminders(self, status: ReminderStatus | str | None = None) -> list[ReminderDefinition]:
        items = list(self._reminders.values())
        if status is not None:
            status_value = status.value if hasattr(status, "value") else str(status)
            items = [item for item in items if item.status.value == status_value]
        return sorted(items, key=lambda item: item.created_at, reverse=True)

    def get_reminder(self, reminder_id: str) -> ReminderDefinition | None:
        return self._reminders.get(reminder_id)

    def cancel_reminder(self, reminder_id: str) -> ReminderDefinition | None:
        reminder = self._reminders.get(reminder_id)
        if reminder is None:
            return None
        reminder.status = ReminderStatus.CANCELLED
        reminder.updated_at = datetime.now(timezone.utc)
        self._reminders[reminder.reminder_id] = reminder
        return reminder

    def add_calendar_draft(self, event: CalendarEventDraft) -> CalendarEventDraft:
        self._calendar_drafts[event.event_id] = event
        return event

    def list_calendar_drafts(self) -> list[CalendarEventDraft]:
        fallback = datetime.min.replace(tzinfo=timezone.utc)
        return sorted(self._calendar_drafts.values(), key=lambda item: item.start_at or fallback, reverse=True)

    def get_calendar_draft(self, event_id: str) -> CalendarEventDraft | None:
        return self._calendar_drafts.get(event_id)

    def cancel_calendar_draft(self, event_id: str) -> CalendarEventDraft | None:
        draft = self._calendar_drafts.get(event_id)
        if draft is None:
            return None
        draft.status = CalendarStatus.CANCELLED
        self._calendar_drafts[draft.event_id] = draft
        return draft

    def clear(self) -> int:
        count = len(self._reminders) + len(self._calendar_drafts)
        self._reminders.clear()
        self._calendar_drafts.clear()
        return count


class LocalJsonAssistantStore(InMemoryAssistantStore):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__()
        self.path = (path or _default_store_path()).resolve()
        self._validate_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _validate_path(self) -> None:
        if self.path.suffix.lower() != ".json":
            raise ValueError("assistant store path must be a .json file")
        lowered_parts = {part.lower() for part in self.path.parts}
        if lowered_parts & BLOCKED_PATH_PARTS:
            raise ValueError("blocked assistant store path")

    def _load(self) -> None:
        if not self.path.exists():
            return
        raw = self.path.read_text(encoding="utf-8").strip()
        if not raw:
            return
        payload = json.loads(raw)
        for item in payload.get("reminders", [])[:MAX_STORED_ITEMS]:
            reminder = ReminderDefinition.model_validate(item)
            self._reminders[reminder.reminder_id] = reminder
        for item in payload.get("calendar_drafts", [])[:MAX_STORED_ITEMS]:
            draft = CalendarEventDraft.model_validate(item)
            self._calendar_drafts[draft.event_id] = draft

    def _save(self) -> None:
        reminders = self.list_reminders()[:MAX_STORED_ITEMS]
        drafts = self.list_calendar_drafts()[:MAX_STORED_ITEMS]
        payload = {
            "reminders": [_sanitize_value(item.model_dump(mode="json")) for item in reminders],
            "calendar_drafts": [_sanitize_value(item.model_dump(mode="json")) for item in drafts],
        }
        temp_path = self.path.with_name(f"{self.path.stem}.{uuid4().hex}.tmp")
        temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        last_error: PermissionError | None = None
        for _ in range(10):
            try:
                temp_path.replace(self.path)
                last_error = None
                break
            except PermissionError as exc:
                last_error = exc
                sleep(0.05)
        if last_error is not None:
            raise last_error

    def add_reminder(self, reminder: ReminderDefinition) -> ReminderDefinition:
        result = super().add_reminder(reminder)
        self._truncate()
        self._save()
        return result

    def cancel_reminder(self, reminder_id: str) -> ReminderDefinition | None:
        result = super().cancel_reminder(reminder_id)
        self._save()
        return result

    def add_calendar_draft(self, event: CalendarEventDraft) -> CalendarEventDraft:
        result = super().add_calendar_draft(event)
        self._truncate()
        self._save()
        return result

    def cancel_calendar_draft(self, event_id: str) -> CalendarEventDraft | None:
        result = super().cancel_calendar_draft(event_id)
        self._save()
        return result

    def clear(self) -> int:
        count = super().clear()
        self._save()
        return count

    def _truncate(self) -> None:
        reminder_ids = [item.reminder_id for item in self.list_reminders()[:MAX_STORED_ITEMS]]
        draft_ids = [item.event_id for item in self.list_calendar_drafts()[:MAX_STORED_ITEMS]]
        self._reminders = {item_id: item for item_id, item in self._reminders.items() if item_id in reminder_ids}
        self._calendar_drafts = {item_id: item for item_id, item in self._calendar_drafts.items() if item_id in draft_ids}


_global_store: InMemoryAssistantStore | None = None


def get_store() -> InMemoryAssistantStore:
    global _global_store
    if _global_store is None:
        _global_store = LocalJsonAssistantStore()
    return _global_store
