# Sprint 49 - Notification / Reminder / Calendar Assistant

## Purpose

Sprint 49 strengthens the personal assistant side of ATLAS with a local-first reminder, notification, and calendar MVP. This sprint stays on a strict preview-only boundary.

## Scope Summary

- local reminder model and local reminder store
- reminder create/list/cancel/preview flows
- local calendar query preview against local drafts only
- local calendar event draft creation
- notification copy / preview model
- `ConversationLoop` integration
- `PermissionPanelService` integration
- `ai reminder`
- `ai calendar`
- optional `ai notification-preview`

## Reminder Model

Core reminder objects:

- `ReminderDefinition`
- `ReminderStatus`
- `ReminderOperation`
- `ReminderOperationResult`
- `ReminderSource`

MVP note:

- `active` does not mean a real running scheduler
- in Sprint 49 it only means a local preview/store state if used later
- no reminder trigger runtime exists

## Calendar Model

Core calendar objects:

- `CalendarQuery`
- `CalendarEventDraft`
- `CalendarOperation`
- `CalendarOperationResult`
- `CalendarStatus`

Model stance:

- `calendar.query` reads only local draft state
- `calendar.event_draft` creates a local draft only
- no Google Calendar
- no Outlook / Graph
- no external write

## Notification Preview Model

Core notification objects:

- `NotificationDraft`
- `NotificationChannel`
- `NotificationStatus`
- `NotificationOperationResult`

Notification scope:

- preview/copy only
- no Windows notification
- no desktop daemon
- no push bridge

## Local-First Boundary

Sprint 49 remains local-first:

- reminder and calendar state stays in memory or safe local JSON
- default JSON path is `workspace/state/personal-assistant.json`
- item count is bounded
- sensitive-looking strings are redacted in persisted JSON
- blocked secret-like content is not stored as a normal reminder/calendar record

## No External Calendar Boundary

Sprint 49 does not add:

- Google Calendar API
- Outlook / Microsoft Graph API
- CalDAV or other sync
- network discovery
- cloud calendar write

`CalendarService` must keep `external_calendar_used=false`.

## No OS Notification Boundary

Sprint 49 does not add:

- Windows toast notification
- tray badge runtime
- reminder popup runtime
- background notifier

`NotificationService` only builds preview copy and keeps `os_notification_sent=false`.

## PermissionPanel Integration

Reminder and calendar draft requests can be queued into the panel backend:

- `ai panel --submit "Bana 20 dakika sonra su icmeyi hatirlat"`
- `ai panel --submit "Yarin 10a toplanti ekle"`

Rules:

- item is preview/confirmation only
- approve changes model state only
- approve does not start a scheduler
- approve does not write to an external calendar

## ConversationLoop Integration

`ConversationLoop` now checks personal assistant patterns before the generic router fallback:

- reminder create -> confirmation-required local preview
- reminder list -> local reminder summary
- calendar query -> safe read-only local preview
- calendar event draft -> confirmation-required local preview
- unknown or unrelated text -> existing memory/routine/device/PC flow continues

## CLI Examples

```powershell
python -m app.cli ai reminder --project ATLAS "Bana 20 dakika sonra su icmeyi hatirlat"
python -m app.cli ai reminder --project ATLAS --list
python -m app.cli ai reminder --project ATLAS --json "Yarin 9da toplantiyi hatirlat"

python -m app.cli ai calendar --project ATLAS "Bugun takvimimde ne var?"
python -m app.cli ai calendar --project ATLAS "Yarin 10a toplanti ekle"
python -m app.cli ai calendar --project ATLAS --list-drafts
python -m app.cli ai calendar --project ATLAS --json "Cuma 14:00e gorusme koy"

python -m app.cli ai notification-preview --project ATLAS --title "Hatirlatma" --body "Su ic"
```

## Privacy / Sensitive Content Policy

Sprint 49 blocks or constrains sensitive content:

- credentials / password / token / secret-like text is blocked
- reminder/calendar text with identity or finance indicators is treated conservatively
- medical-style text may be kept local preview only with warnings
- no `.env` or credential source is read

## Test Plan

Validation targets:

- reminder/calendar/notification models instantiate
- parser matches Turkish reminder/calendar patterns
- sensitive reminder content is blocked
- reminder create returns pending confirmation
- calendar query stays local-only
- calendar draft returns pending confirmation
- panel approval stays non-executing
- CLI JSON payloads are valid
- regression suite still passes for chat/panel/home-preview/voice/routine

## Acceptance Criteria

- `app/personal_assistant` exists
- reminder/calendar/notification models exist
- local preview services exist
- `ai reminder` works
- `ai calendar` works
- `ConversationLoop` reminder/calendar support works
- panel can queue reminder/calendar items
- no OS notification
- no background scheduler
- no external calendar API
- no credential or `.env` read path

## Next Dependency

Sprint 50 should deliver the **End-to-End Personal Assistant Demo** on top of this local-first preview foundation.
