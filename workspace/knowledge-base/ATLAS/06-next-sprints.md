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

## Sprint 51 - Completed

**Goal:** Harden the V1 demo without opening real execution.

Completed:

- central safety invariant suite
- latency measurement and typed report
- `ai hardening` CLI
- panel confirmation timeout / cancel policy
- stricter voice confirmation runtime wording
- Turkish preview UX polish
- docs cleanup and artifact policy clarification

Acceptance outcome:

- preview-only safety boundary preserved
- hardening CLI works for safety, latency, JSON, Markdown, and no-write paths
- demo and regression surfaces remain operational

## Sprint 52 - Safe Execution Gate / Low-Risk PC Execution Planning

**Goal:** Define the first bounded execution gate for a very small low-risk PC allowlist.

Planned scope:

- execution gate contract
- low-risk PC allowlist
- audit requirements
- rollback / failure expectations
- panel-to-execution handoff policy

Still out of scope:

- unrestricted shell
- real home/device write execution
- reminder scheduler
- wake word / always-listening
- external calendar write

## Sprint 53 - Desktop UX Shell

Candidate scope after Sprint 52 only:

- desktop panel shell
- clearer pending approval visibility
- local status surfaces
- no autonomous background execution

## Sprint 54 - Reminder Runtime Planning

Candidate scope after execution gate and desktop policy are stable:

- safe scheduler planning
- stale reminder handling
- local notification authenticity rules

## Roadmap Rule

Every next sprint must preserve:

- explicit permission gate
- preview-first behavior
- no secret reading
- no unrestricted execution
