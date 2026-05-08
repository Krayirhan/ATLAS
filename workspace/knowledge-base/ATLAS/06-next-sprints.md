# ATLAS - Next Sprints

## Completed Foundation

- Sprint 25: V1 RC documentation and usage guide
- Sprint 26: Test coverage hardening
- Sprint 27-34: Read-only AI/agent support layers
- Sprint 35: Read-only AI/agent workflow consolidation
- Sprint 36: Product realignment
- Sprint 37: Intent / Action schema
- Sprint 38: PermissionManager
- Sprint 39: IntentRouter MVP
- Sprint 40: PC preview adapter MVP
- Sprint 41: ConversationLoop MVP
- Sprint 42: Personal memory MVP
- Sprint 43: Routine preview MVP
- Sprint 44: Voice architecture
- Sprint 45: Mock STT/TTS voice pipeline
- Sprint 46: Device registry + room model
- Sprint 47: Home preview adapter
- Sprint 48: Permission panel backend
- Sprint 49: Reminder / calendar / notification preview
- Sprint 50: End-to-end personal assistant demo
- Sprint 51: Safety / Latency / UX Hardening
- Sprint 52: Safe Execution Gate / Low-Risk PC Execution Planning

## Sprint 52 - Completed

**Goal:** Define the first bounded execution gate for a very small low-risk PC allowlist without opening real runtime execution.

Completed:

- `app/execution` package and typed execution contracts
- low-risk allowlist model
- Safe Execution Gate policy and audit metadata
- panel approved item to execution candidate handoff
- `ai execution` CLI
- disabled-by-default executor result
- execution regressions and docs update

Acceptance outcome:

- allowlist exists
- `PowerShell` / `cmd` / unrestricted shell remain blocked
- panel handoff is explicit
- `execution_enabled=false` remains the default
- real app launch still does not happen

## Sprint 53 - Low-Risk PC Execution MVP

Planned scope:

- open a very small runtime path for approved low-risk app opens only
- keep allowlist canonical and path-free
- audit every runtime attempt
- preserve no-shell and no-freeform-command guarantees
- preserve panel approval boundary and rollback expectations

Still out of scope:

- unrestricted shell
- free-form path execution
- real home/device write execution
- reminder scheduler
- wake word / always-listening
- external calendar write

## Sprint 54 - Real Push-to-Talk STT/TTS Integration Planning

Candidate scope after Sprint 53 only:

- microphone privacy model
- push-to-talk session model
- transcript confidence and retry policy
- no wake word runtime yet

## Sprint 55 - Desktop Tray Runtime MVP

Candidate scope after Sprint 53 and Sprint 54 only:

- tray shell planning
- local status and approval visibility
- no autonomous background execution

## Roadmap Rule

Every next sprint must preserve:

- explicit permission gate
- preview-first behavior
- no secret reading
- no unrestricted execution
