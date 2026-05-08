# Sprint 48 - Desktop Permission Panel

## Purpose

Sprint 48 adds the backend and CLI visibility layer for pending confirmations, blocked actions, clarification-needed requests, and audit-friendly preview state. This sprint does not add a real tray runtime or any real action execution.

## Permission Panel Backend

Sprint 48 introduces:

- `app/panel` package
- panel item and decision models
- pending queue store
- model-only approve / deny / cancel flow
- CLI access through `ai panel`

This backend is the contract layer that a future tray UI can consume.

## CLI Panel MVP

Supported flows:

```powershell
python -m app.cli ai panel --project ATLAS --submit "Salon isigini ac"
python -m app.cli ai panel --project ATLAS --submit "Isigi ac"
python -m app.cli ai panel --project ATLAS --submit "Sifrelerimi oku"
python -m app.cli ai panel --project ATLAS --submit "Bana 20 dakika sonra su icmeyi hatirlat"
python -m app.cli ai panel --project ATLAS --submit "Yarin 10a toplanti ekle"
python -m app.cli ai panel --project ATLAS --list
python -m app.cli ai panel --project ATLAS --show ITEM_ID
python -m app.cli ai panel --project ATLAS --approve ITEM_ID
python -m app.cli ai panel --project ATLAS --deny ITEM_ID
python -m app.cli ai panel --project ATLAS --cancel ITEM_ID
python -m app.cli ai panel --project ATLAS --json --list
```

## Pending Confirmation List

Queue item classes:

- action preview
- confirmation required
- clarification required
- blocked
- reminder confirmation preview
- calendar draft confirmation preview
- denied
- approved preview
- cancelled

Each item must show:

- summary
- action type
- target
- risk
- source
- warnings
- confirmation prompt when relevant
- created time
- expiry
- audit metadata

## Risk Badges

Minimum badge set:

- `safe_readonly`
- `low`
- `medium`
- `high`
- `blocked`

The UI layer should display risk clearly before any approval action is offered.

## Approve / Deny / Cancel UX

Sprint 48 behavior:

- approve updates model state only
- approve does not run execution
- approve does not schedule a reminder
- approve does not write an external calendar event
- deny updates model state only
- cancel updates model state only
- blocked items cannot be approved
- clarification-required items cannot be approved
- expired items cannot be approved

## Preview vs Execution Copy

Every CLI/detail surface should repeat the same rule:

`Bu sadece onizlemedir, islem calistirilmadi.`

This distinction is mandatory because the product still has no real PC/home execution path.

## Audit / Log Panel Direction

Future desktop surfaces should expose:

- pending items
- recently denied items
- recently cancelled items
- blocked reasons
- audit timestamps
- adapter/source context

Sprint 48 keeps this at backend and CLI level only.

## Notification Strategy

Notification behavior is deferred, but the future panel should be able to:

- raise a local notification for new confirmation-required items
- show blocked actions without implying execution
- expire stale items

Sprint 49 adds notification copy previews for reminder/calendar flows, but it still does not add OS notifications.

## Security Rules

- no execution after approve
- no tray daemon
- no background listener
- no network dependency
- no credential loading
- no sensitive raw prompt retention
- no approval replay

## No-Execution Boundary

Sprint 48 does not add:

- real desktop tray runtime
- GUI framework
- PC execution
- home execution
- Home Assistant or MQTT
- terminal executor

## Future Real Tray Requirements

Before a real tray runtime is allowed:

- explicit startup policy
- visible pending badge logic
- trustworthy notification copy
- stale-item expiry handling
- audit/log browsing
- confirmation replay prevention
- execution handoff policy

## Acceptance Criteria

- `app/panel` exists
- `ai panel` works
- submit/list/show works
- approve/deny/cancel update state only
- blocked/clarification items cannot be approved
- local store is bounded and safe
- tray runtime is not implemented

## Sprint 49 Integration

Sprint 49 now connects the panel backend to reminder and calendar preview flows:

- `ai panel --submit "Bana 20 dakika sonra su icmeyi hatirlat"` creates a confirmation item
- `ai panel --submit "Yarin 10a toplanti ekle"` creates a calendar draft confirmation item
- approve still leaves `execution_attempted=false`
- no scheduler, no OS notification, and no external calendar write starts after approval

## Next Dependency

Sprint 50 should deliver an **End-to-End Personal Assistant Demo** that shows the reminder/calendar preview flow next to safe PC, routine, and voice preview paths.
