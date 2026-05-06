# ATLAS PC Control Adapter Design

## Purpose

PC Control is the first personal action target for ATLAS. This document defines safe MVP actions and deferred risky actions.

No PC control runtime is implemented in Sprint 36.

## Adapter Boundary

The PC Control Adapter executes only approved actions from ActionRouter and PermissionManager.

```text
ActionRouter -> PermissionManager -> PCControlAdapter -> Result/Audit
```

The adapter does not interpret natural language directly.

## Safe MVP Actions

| Action | Risk level | Dry-run support | Approval needed | Test approach |
|---|---|---|---|---|
| `pc.open_app` | low | yes | no in later phase, preview first in MVP | mock app registry, verify selected app id |
| `pc.open_folder` | low/medium | yes | confirm if personal/user folder | mock path resolver, blocked path tests |
| `pc.system_info` | low | yes | no | mocked system info provider |
| `pc.media.play_pause` | low | yes | no | mocked media backend |
| `pc.volume.set` | medium | yes | yes for large jumps | boundary tests for volume range |
| `browser.search` | low/medium | yes | confirm for sensitive query if needed | mock browser adapter |
| `pc.file_search_preview` | low/medium | yes | confirm if personal/sensitive scope | safe path and blocked pattern tests |

## Risky / Later Actions

| Action category | Status | Reason |
|---|---|---|
| delete file | blocked/deferred | irreversible data loss |
| recursive delete | blocked | high destructive risk |
| shutdown/restart | deferred/high | interrupts work |
| install app | deferred/high | system change and supply-chain risk |
| registry edit | blocked | system damage risk |
| admin commands | blocked/deferred | privilege and damage risk |
| background automation | deferred | invisible side effects |
| clipboard write | medium/deferred | privacy and surprise risk |
| screenshot/vision | later | privacy and sensitive data risk |

## Path Safety

Rules:

- `D:\ATLAS` is blocked.
- `C:\Users` full scan is blocked.
- `.env`, keys, keystores, browser profiles are blocked.
- File search must use preview mode first.
- Folder open must not imply recursive reading.

## Approval Policy

Initial handling:

- read-only info actions: low
- visible local UI action: low/medium
- personal data path: medium
- destructive/system-level action: high or blocked
- unknown action: approval required or blocked

## Result Model

PC action result should include:

- action type
- target
- adapter
- status
- user-visible summary
- warnings
- audit id

## MVP Acceptance Criteria

- Every PC control action has a schema entry.
- Every action has a risk level.
- Dry-run is available for all MVP actions.
- Blocked paths and secret patterns are enforced.
- No destructive action is in MVP execution scope.
