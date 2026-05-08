# ATLAS Assistant Architecture

## Purpose

This document captures the preview-first architecture for ATLAS after Sprint 51 hardening.

## Canonical Flow

```text
User input
  -> ConversationLoop
  -> IntentRouter / PersonalAssistantService
  -> ActionCandidate + PermissionDecision
  -> Preview planner (PC / device / home / routine / reminder / calendar / panel)
  -> Safety + latency hardening
  -> User-facing response / report
```

## Runtime Layers

| Layer | Current status |
|---|---|
| Interaction | CLI text plus mock voice |
| Conversation | Implemented |
| Intent / permission | Implemented preview-only |
| PC preview | Implemented |
| Device / home preview | Implemented |
| Reminder / calendar preview | Implemented |
| Panel backend | Implemented |
| Demo runner | Implemented |
| Quality hardening | Implemented in Sprint 51 |
| Real execution gate | Not implemented |

## Sprint 51 Quality Layer

`app/quality` adds a new hardening layer:

- safety suite
- latency suite
- hardening report models
- Markdown / JSON formatter
- `ai hardening` CLI

This layer does not execute actions. It measures deterministic preview surfaces only.

## Voice Safety Architecture

Voice stays on the same permission path as text:

```text
mock transcript
  -> MockSTTAdapter
  -> transcript confidence check
  -> ConversationLoop
  -> PermissionManager
  -> runtime voice safety copy
```

Rules:

- low-confidence transcript -> clarification
- medium/high voice request -> explicit confirmation
- high-risk voice request -> short `evet` not enough
- real microphone capture remains disabled

## Panel Confirmation Architecture

Panel items now carry explicit timeout policy:

- `default_timeout_seconds`
- `expires_at`
- expired item cannot be approved
- cancelled item cannot be approved
- denied item cannot be approved
- blocked item cannot be approved
- clarification-required item cannot be approved
- approve never starts execution

## Execution Boundary

Sprint 51 still forbids:

- real PC execution
- real home execution
- scheduler / daemon runtime
- OS notification delivery
- external calendar writes
- microphone capture
- wake word / always-listening
- shell / terminal execution

## Next Dependency

Sprint 52 may add a bounded execution gate only after these contracts stay stable.
