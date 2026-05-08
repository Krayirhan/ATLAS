from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ReminderStatus(str, Enum):
    DRAFT = "draft"
    PENDING_CONFIRMATION = "pending_confirmation"
    SCHEDULED_PREVIEW = "scheduled_preview"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class ReminderOperation(str, Enum):
    CREATE = "create"
    LIST = "list"
    SHOW = "show"
    CANCEL = "cancel"
    PREVIEW = "preview"
    UNKNOWN = "unknown"


class ReminderResultStatus(str, Enum):
    PENDING_CONFIRMATION = "pending_confirmation"
    LISTED = "listed"
    SHOWN = "shown"
    CANCELLED = "cancelled"
    PREVIEW = "preview"
    BLOCKED = "blocked"
    NOT_FOUND = "not_found"
    INVALID = "invalid"
    UNSUPPORTED = "unsupported"


class ReminderSource(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    ROUTINE = "routine"
    SCHEDULE = "schedule"
    MANUAL = "manual"
    UNKNOWN = "unknown"


class ReminderDefinition(BaseModel):
    reminder_id: str
    title: str
    message: str
    due_at_text: str = ""
    due_at: datetime | None = None
    timezone: str = "Europe/Istanbul"
    recurrence: str = ""
    source: ReminderSource = ReminderSource.TEXT
    status: ReminderStatus = ReminderStatus.DRAFT
    requires_confirmation: bool = True
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReminderOperationResult(BaseModel):
    status: ReminderResultStatus
    operation: ReminderOperation
    reminder: ReminderDefinition | None = None
    reminders: list[ReminderDefinition] = Field(default_factory=list)
    message: str = ""
    warnings: list[str] = Field(default_factory=list)
    blocked_reason: str | None = None
    audit_metadata: dict[str, Any] = Field(default_factory=dict)


class CalendarQuery(BaseModel):
    query_id: str
    query_text: str
    date_text: str = ""
    range_start: datetime | None = None
    range_end: datetime | None = None
    source: ReminderSource = ReminderSource.TEXT
    metadata: dict[str, Any] = Field(default_factory=dict)


class CalendarStatus(str, Enum):
    SAFE_QUERY_PREVIEW = "safe_query_preview"
    DRAFT_CREATED = "draft_created"
    PENDING_CONFIRMATION = "pending_confirmation"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    UNSUPPORTED = "unsupported"
    LISTED = "listed"
    NOT_FOUND = "not_found"


class CalendarEventDraft(BaseModel):
    event_id: str
    title: str
    start_text: str = ""
    start_at: datetime | None = None
    end_text: str = ""
    end_at: datetime | None = None
    location: str = ""
    notes: str = ""
    attendees: list[str] = Field(default_factory=list)
    source: ReminderSource = ReminderSource.TEXT
    requires_confirmation: bool = True
    status: CalendarStatus = CalendarStatus.PENDING_CONFIRMATION
    metadata: dict[str, Any] = Field(default_factory=dict)


class CalendarOperation(str, Enum):
    QUERY = "query"
    DRAFT_EVENT = "draft_event"
    LIST_LOCAL = "list_local"
    CANCEL_DRAFT = "cancel_draft"
    UNKNOWN = "unknown"


class CalendarOperationResult(BaseModel):
    status: CalendarStatus
    operation: CalendarOperation
    query: CalendarQuery | None = None
    event_draft: CalendarEventDraft | None = None
    event_drafts: list[CalendarEventDraft] = Field(default_factory=list)
    message: str = ""
    warnings: list[str] = Field(default_factory=list)
    blocked_reason: str | None = None
    audit_metadata: dict[str, Any] = Field(default_factory=dict)


class NotificationChannel(str, Enum):
    CLI = "cli"
    FUTURE_DESKTOP = "future_desktop"
    FUTURE_OS = "future_os"
    FUTURE_MOBILE = "future_mobile"
    UNKNOWN = "unknown"


class NotificationStatus(str, Enum):
    PREVIEW = "preview"
    QUEUED_PREVIEW = "queued_preview"
    BLOCKED = "blocked"
    UNSUPPORTED = "unsupported"


class NotificationDraft(BaseModel):
    notification_id: str
    title: str
    body: str
    channel: NotificationChannel = NotificationChannel.CLI
    priority: str = "normal"
    source: ReminderSource = ReminderSource.TEXT
    status: NotificationStatus = NotificationStatus.PREVIEW
    created_at: datetime = Field(default_factory=_utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class NotificationOperationResult(BaseModel):
    status: NotificationStatus
    notification: NotificationDraft | None = None
    message: str = ""
    warnings: list[str] = Field(default_factory=list)
    audit_metadata: dict[str, Any] = Field(default_factory=dict)
