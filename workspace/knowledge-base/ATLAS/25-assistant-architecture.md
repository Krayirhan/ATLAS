# ATLAS Assistant Architecture

## Purpose

This document captures the preview-first architecture for ATLAS after Sprint 52 Safe Execution Gate planning.

## Canonical Flow

```text
User input
  -> ConversationLoop
  -> IntentRouter / PersonalAssistantService
  -> ActionCandidate + PermissionDecision
  -> Preview planner (PC / device / home / routine / reminder / calendar / panel)
  -> Safe Execution Gate planning (optional, disabled by default)
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
| Safe Execution Gate | Implemented planning-only in Sprint 52 |
| Device / home preview | Implemented |
| Reminder / calendar preview | Implemented |
| Panel backend | Implemented |
| Demo runner | Implemented |
| Quality hardening | Implemented in Sprint 51 |
| Real execution runtime | Not implemented |

## Safe Execution Gate Layer

`app/execution` adds a bounded planning layer:

- typed execution models
- low-risk allowlist
- policy evaluation
- panel-to-execution handoff
- disabled executor result
- audit metadata with `execution_attempted=false`

Canonical sub-flow:

```text
PC preview or approved panel item
  -> ExecutionPlan
  -> ExecutionGate.evaluate()
  -> ExecutionDecision
  -> ExecutionGate.prepare_*()
  -> disabled / not_approved / unsupported / blocked result
```

Rules:

- `execution_enabled=false` by default
- `execute()` does not launch apps or processes
- no PowerShell, cmd, or unrestricted shell
- no free-form path execution
- no direct user text to command string mapping

## Sprint 51 Quality Layer

`app/quality` still measures deterministic preview surfaces only:

- safety suite
- latency suite
- hardening report models
- Markdown / JSON formatter
- `ai hardening` CLI

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

Panel items now carry explicit timeout policy and execution handoff constraints:

- `default_timeout_seconds`
- `expires_at`
- expired item cannot be approved
- cancelled item cannot be approved
- denied item cannot be approved
- blocked item cannot be approved
- clarification-required item cannot be approved
- approve never starts execution
- approved item may become an execution candidate only through `ExecutionGate`

## Execution Boundary

Sprint 52 still forbids:

- real PC execution
- real home execution
- scheduler / daemon runtime
- OS notification delivery
- external calendar writes
- microphone capture
- wake word / always-listening
- shell / terminal execution

## Next Dependency

Sprint 53 may open only a very small low-risk PC runtime under this gate. The architectural boundary remains explicit and audited.
