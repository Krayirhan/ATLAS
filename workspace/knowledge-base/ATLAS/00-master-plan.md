# ATLAS Master Plan - Personal Control Assistant Architecture

> Root: `E:\ATLAS`  
> Primary platform: Windows  
> Sprint: 36 - Product Realignment & Assistant Architecture  
> Direction: local-first personal control assistant foundation

## 1. Product Vision

ATLAS is a local-first personal AI assistant foundation for Windows. It uses Ollama as the default local LLM runtime and is designed to understand text and future voice commands, then safely manage personal PC actions, personal knowledge, routines, and device/home automation through explicit permission and audit controls.

ATLAS is not primarily a developer assistant. Developer-oriented modules built so far remain useful support infrastructure, but the main product path is the personal control assistant.

## 2. Legacy Direction

Earlier development built a strong devtools/control-plane foundation. These modules are preserved as support infrastructure but are no longer the primary product direction.

Preserved legacy value:

- Python CLI control plane
- config validation
- project registry
- safety policy
- MCP config generation
- SQLite memory foundation
- bounded AI context
- Ollama provider
- read-only agent contracts
- approval evaluator
- doctor, tests, and audit flow

Parked legacy/devtools direction:

- code review as a user-facing priority
- documentation audit as primary roadmap
- report synthesis as primary roadmap
- Git hygiene sprint as near-term priority
- CodeBuilder/BugFix/Refactor autonomous coding ideas
- broad developer automation

## 3. Local-First Principles

ATLAS must remain local-first by default:

- Default LLM path is local Ollama on loopback.
- Core state lives under `E:\ATLAS`.
- No cloud API key is required for the default assistant loop.
- No `.env`, private key, SSH key, keystore, browser profile, or raw secret source enters prompt context.
- `D:\ATLAS` is not an operational root.
- MCP filesystem exposure remains bounded to `E:\ATLAS\workspace`.
- Raw logs with possible secrets are not model context.
- NotebookLM is optional/manual knowledge workflow, not runtime dependency.

## 4. Voice and Text Interaction

Initial interaction is text-first, then push-to-talk voice. Wake word is deferred until privacy controls, microphone state UX, local processing rules, and confirmation rules are ready.

Interaction stages:

1. Text command and CLI-assisted assistant loop.
2. Push-to-talk voice command.
3. STT/TTS MVP.
4. ConversationLoop with cancel/interruption.
5. Future wake word after privacy acceptance.

Voice requirements:

- Turkish command quality must be measured.
- Misheard commands must not execute risky actions.
- Medium/high risk actions require confirmation.
- User can cancel before execution.
- Text fallback must always exist.

## 5. Canonical Runtime Flow

```text
User input
  -> ConversationLoop
  -> IntentRouter
  -> MainAgent
  -> CommandUnderstandingAgent
  -> ActionRouter
  -> PermissionManager
  -> Adapter
  -> Result/Audit
  -> TTS/UI response
```

Flow rules:

- Intent extraction does not execute.
- Action routing does not execute.
- PermissionManager decides whether preview, confirmation, or block is required.
- Adapters execute only approved safe actions.
- Every action result is audited.

## 6. Assistant Runtime Layers

| Layer | Responsibility |
|---|---|
| Interaction Layer | Text, push-to-talk voice, future wake word, future desktop/mobile UI |
| AI Reasoning Layer | Ollama-backed reasoning with bounded context |
| Memory Layer | Personal preferences, device aliases, routines, safe command history |
| Intent/Action Layer | Intent schema, action schema, action router, skill registry |
| Permission Layer | Risk classification, preview, confirmation, blocked actions |
| Adapter Layer | PC control, browser/media/files, future home/device actions |
| Audit Layer | Decision, execution result, warnings, source metadata |
| UI Layer | Future tray, permission panel, logs, settings, routine editor |

## 7. PC Control MVP

PC Control is the first action target because it is local, Windows-focused, and directly aligned with the personal assistant goal.

Safe MVP actions:

- open app
- open folder
- show system info
- media play/pause
- volume control
- browser search
- file search preview

Deferred or blocked actions:

- delete files
- shutdown/restart
- install applications
- registry edits
- admin commands
- background automation without visible confirmation

## 8. Home Control Later

Home control is a later layer because physical device control has higher risk.

Design stance:

- Home Assistant is the first candidate integration.
- MQTT is an alternative integration path.
- Cloud providers are later and optional.
- DeviceRegistry and Room Model must exist first.
- State read can come before state write.
- No physical device action runs until PermissionManager and action audit are ready.

## 9. Routine Engine

RoutineEngine turns repeated personal workflows into previewable and auditable action groups.

Routine examples:

- calisma modu
- oyun modu
- uyku modu
- toplanti modu
- evden cikiyorum
- eve geldim

Routine requirements:

- routine definition
- routine preview
- schedule or manual trigger
- conditional trigger later
- action grouping
- confirmation for medium/high risk steps
- result/audit summary

## 10. Personal Memory

Personal memory is not raw log ingestion. It must be intentional, scoped, and deletable.

Memory categories:

- personal preferences
- device aliases
- room names
- routine definitions
- safe command history summaries
- notification/reminder preferences

Privacy requirements:

- sensitive memory labels
- forget/delete mechanism
- export/backup policy
- no secret ingestion
- no raw browser profile or raw log ingestion

## 11. Safety Model

Risk levels:

| Risk | Meaning | Default handling |
|---|---|---|
| low | Read-only or easily reversible | preview optional; auto only in later phases |
| medium | Changes local state or triggers visible behavior | explicit confirmation |
| high | Could disrupt work, privacy, devices, or irreversible state | confirmation plus warning |
| blocked | Forbidden by policy or too risky | no execution |

Safety rules:

- Irreversible actions are high or blocked.
- Voice-originated actions are more conservative until confidence metrics exist.
- Unknown actions require manual review.
- Home/device write actions require device identity, room, capability, and confirmation.
- All executed actions produce audit metadata.

## 12. Existing Module Repositioning

| Module | New role |
|---|---|
| Ollama provider | Core local LLM runtime |
| Mock provider | Deterministic tests and fallback |
| AIContextLoader | Bounded context source foundation |
| PromptComposer | Safe reasoning prompt foundation |
| MemoryAgent | Foundation for PersonalMemoryAgent |
| ProjectQAAgent | Foundation for Personal Knowledge QA |
| PlannerAgent | Reposition as Routine/Task Planner foundation |
| MainAgent | Assistant coordinator around future intent/action routing |
| ToolApprovalAgent | Foundation for PermissionManager |
| SecurityAuditorAgent | Safety auditor for AI, PC, home, privacy |
| CodeReviewerAgent | Parked devtools support |
| DocumentationAgent | Supporting knowledge hygiene |
| ReportAgent | Parked ops/devtools reporting |

## 13. Roadmap Sprint 36-51

| Sprint | Focus |
|---|---|
| Sprint 36 | Product Realignment & Assistant Architecture |
| Sprint 37 | Action Architecture & Intent Schema |
| Sprint 38 | PermissionManager & Action Approval Flow |
| Sprint 39 | IntentRouter MVP |
| Sprint 40 | PC Control Adapter MVP |
| Sprint 41 | ConversationLoop MVP |
| Sprint 42 | Personal Memory & Preferences |
| Sprint 43 | RoutineEngine MVP |
| Sprint 44 | Voice Core Architecture |
| Sprint 45 | STT/TTS MVP |
| Sprint 46 | DeviceRegistry + Room Model |
| Sprint 47 | Home Control Adapter Design |
| Sprint 48 | Desktop Tray / Permission Panel |
| Sprint 49 | Notification / Reminder / Calendar Assistant |
| Sprint 50 | End-to-End Personal Assistant Demo |
| Sprint 51 | Safety / Latency / UX Hardening |

## 14. Parked Developer Tools

These items are not removed. They are parked so they do not drive the product roadmap:

- CodeReviewerAgent
- DocumentationAgent as project-doc audit
- ReportAgent/report expansion
- Git Hygiene
- TestWriterAgent
- BugFixAgent
- CodeBuilderAgent
- RefactorAgent
- autonomous coding
- developer-only RAG/vector index

They can remain as maintenance tools for ATLAS itself, but they must not be treated as the main assistant product.

## 15. Sprint 36 Acceptance Criteria

- README reflects the personal control assistant target.
- `assistant-core/README.md` documents current and future technical layers.
- Current status separates completed core, parked devtools, and missing personal assistant layers.
- Next sprints use Sprint 37-51 personal assistant roadmap.
- Product realignment and architecture docs 24-31 exist.
- No Python logic is changed by this sprint.
- Validation commands pass or are documented as conditional.
