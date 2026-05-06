# Sprint 39 - IntentRouter MVP

## Purpose

Sprint 39 builds the first deterministic routing layer that turns user text into safe personal action previews.

## IntentRouter Role

`IntentRouter` is responsible for:

- parsing text into `IntentResult`
- extracting basic entities
- mapping intent to `ActionCandidate`
- calling `PermissionManager` for preview decisions
- keeping ambiguous, unknown, and blocked requests on safe non-executing paths

## Rule-Based MVP Approach

Sprint 39 is deterministic:

- no LLM call
- no Ollama dependency
- regex and string matching only
- explicit fallback to clarification or unknown

## Intent Categories

MVP covers:

- `conversation.question`
- `conversation.status`
- `pc.open_app`
- `pc.open_folder`
- `pc.system_info`
- `pc.media_control`
- `pc.volume_control`
- `browser.search`
- `file.search`
- `reminder.create`
- `routine.run`
- `device.turn_on`
- `device.turn_off`
- `device.set_temperature`
- `blocked`
- `ambiguous`
- `unknown`

## Entity Extraction

MVP entities:

- `app_name`
- `folder_name`
- `query`
- `reminder_text`
- `date_time_text`
- `routine_name`
- `room_name`
- `device_name`
- `temperature`
- `volume_level`

## Intent to ActionCandidate Mapping

Examples:

- `Chrome'u ac` -> `pc.open_app` -> `pc.open_app`
- `Belgeler klasorunu ac` -> `pc.open_folder` -> `pc.open_folder`
- `Bilgisayar bilgilerini goster` -> `pc.system_info` -> `pc.system_info`
- `PDF dosyalarimi bul` -> `file.search` -> `file.search`
- `Bana 20 dakika sonra su icmeyi hatirlat` -> `reminder.create` -> `reminder.create`
- `Calisma modunu baslat` -> `routine.run` -> `routine.run`
- `Salon isigini ac` -> `device.turn_on` -> `device.turn_on`
- `Bilgisayari kapat` -> high-risk `pc.shutdown` preview
- `Sifrelerimi oku` -> blocked `secret.read`

## Ambiguous and Unknown Fallback

Ambiguous examples:

- `Isigi ac`
- `Kapat`
- `Modu baslat`
- `Sesi ayarla`

Behavior:

- `IntentResult.requires_clarification=true`
- clarification question is produced
- no execution path exists

Unknown examples:

- unsupported phrasing
- low-signal random text
- text that does not map safely to a known category

Behavior:

- `category=unknown`
- clarification or no-action response
- no adapter path

## PermissionManager Integration

Preview flow:

```text
user text
  -> IntentRouter.parse_text()
  -> IntentResult
  -> IntentRouter.to_action_candidate()
  -> ActionCandidate
  -> PermissionManager.build_preview()
  -> PermissionManager.decide()
  -> IntentPreviewResult
```

## CLI Preview Examples

```powershell
python -m app.cli ai intent --project ATLAS "Chrome'u ac"
python -m app.cli ai intent --project ATLAS --show-preview "Salon isigini ac"
python -m app.cli ai intent --project ATLAS --show-preview "Isigi ac"
python -m app.cli ai intent --project ATLAS --json "Sifrelerimi oku"
```

## Execution Boundary

Sprint 39 still does not implement:

- PC control execution
- home control execution
- browser opening
- media control execution
- terminal or PowerShell execution
- adapters
- voice runtime

## Test Plan

- router classification tests
- entity extraction tests
- blocked/ambiguous/unknown tests
- permission integration tests
- CLI output tests
- regression tests for existing action and permission contracts

## Acceptance Criteria

- user text routes to `IntentResult`
- `IntentResult` maps to `ActionCandidate`
- PermissionManager integration works
- `ai intent` previews route safely
- blocked and ambiguous requests remain non-executing
- all tests pass

## Sprint 40 Dependency

Sprint 40 should implement **PC Control Adapter MVP** and consume approved low/safe preview outputs without bypassing IntentRouter or PermissionManager.
