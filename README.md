# ATLAS AI Assistant

## Product Vision

ATLAS is a local-first personal AI assistant foundation for Windows. It is designed to understand voice and text commands, use Ollama as the default local LLM runtime, and safely manage personal computer actions, personal knowledge, routines, and device or home automation actions through an explicit permission and approval model.

ATLAS is not primarily a developer assistant. The current developer-oriented agents remain valuable as a devtools/supporting subsystem, but the main product direction is now the personal control assistant architecture.

## Current Status

| Item | Value |
|---|---|
| Product direction | Personal control assistant foundation |
| Release baseline | V1 RC - GO for the existing local control plane |
| Sprint focus | Sprint 45 - STT/TTS MVP completed; Sprint 46 next |
| Root | `E:\ATLAS` |
| Assistant core | `E:\ATLAS\assistant-core` |
| Knowledge base | `E:\ATLAS\workspace\knowledge-base\ATLAS` |
| Default LLM provider | `ollama` |
| Test command | `python -m pytest -q` from `assistant-core` |
| Health command | `python -m app.cli doctor --full` |

The existing V1 control plane is technically healthy: config validation, project registry, safety policy, MCP config generation, bounded AI context, read-only agents, doctor, tests, and release audit are in place.

The missing product layers are real microphone capture, real local STT/TTS engines, ActionRouter, device registry, home control, permission UI, desktop panel, durable scheduling, and mobile bridge.

## Core Architecture

ATLAS now separates the project into three tracks:

1. **Core assistant foundation**
   - local LLM runtime
   - bounded context loading
   - main assistant orchestration
   - action approval foundation
   - security audit foundation
   - local configuration and audit

2. **Personal control assistant product track**
   - voice and text interaction
   - intent understanding
   - action routing
   - permission and confirmation UX
   - Windows PC control
   - routines
   - personal memory
   - home/device automation

3. **Parked devtools subsystem**
   - read-only code review
   - documentation audit
   - report synthesis
   - repo hygiene ideas
   - coding automation ideas

## Assistant Runtime Layers

Target runtime flow:

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

Target layers:

| Layer | Responsibility |
|---|---|
| Interaction Layer | Text, push-to-talk voice, future wake word, future desktop/mobile UI |
| AI Reasoning Layer | Ollama-backed reasoning, bounded prompt/context |
| Memory Layer | Personal preferences, routines, device aliases, safe command history |
| Intent/Action Layer | Intent schema, action schema, skill registry, action router |
| Permission Layer | Risk classification, preview, confirmation, block rules |
| Adapter Layer | PC control, browser, media, files, future home/device adapters |
| Audit Layer | Action result, decision trail, security review evidence |
| UI Layer | Future tray, permission panel, logs, settings, routine editor |

## Safety & Permission Model

ATLAS remains security-first. The personal assistant must follow this sequence:

```text
understand -> preview -> classify risk -> ask approval if needed -> execute only allowed action -> audit result
```

Baseline rules:

- No full-disk MCP exposure.
- No `.env`, private key, SSH key, keystore, browser profile, or raw secret source reading.
- No `D:` writes as ATLAS policy stance.
- No unrestricted terminal execution.
- No git push or production deployment automation in the assistant path.
- Medium and high risk actions require explicit confirmation.
- Blocked actions must not execute.
- Voice commands must be treated as potentially misheard until confidence and confirmation rules exist.

## Existing AI/Agent Core

These modules are preserved as core or foundation infrastructure:

- `app/ai`: local LLM runtime, Ollama provider, mock provider, context loader, prompt composer, AI service.
- `app/actions`: Sprint 37 intent/action/risk/result contracts, Sprint 38 PermissionManager, and Sprint 39 deterministic IntentRouter preview flow; no execution or adapter code.
- `MemoryAgent`: project-memory foundation; will evolve toward personal memory.
- `ProjectQAAgent`: project QA foundation; will evolve toward personal knowledge QA.
- `PlannerAgent`: planning foundation; will be repositioned as routine/task planning.
- `MainAgent`: current deterministic coordinator; will become the assistant coordination layer around intent/action routing.
- `ToolApprovalAgent`: devtools command/tool preview foundation.
- `PermissionManager`: personal action preview, confirmation, block, clarification, and audit metadata foundation.
- `IntentRouter`: deterministic text-to-intent and intent-to-action-candidate preview foundation.
- `SecurityAuditorAgent`: security audit foundation; will expand to PC/home/privacy risk checks.

All current agents remain read-only. They do not write files, run terminal commands, call MCP tools, or produce approval tokens.

## Parked DevTools Subsystem

The following work is not deleted, but it is no longer on the main product path:

| Item | New status | Reason |
|---|---|---|
| `CodeReviewerAgent` | Parked devtools support | Useful for repo quality, not personal assistant runtime |
| `DocumentationAgent` | Supporting knowledge hygiene | Useful for KB/README consistency, not core user workflow |
| `ReportAgent` idea/current work | Parked reporting support | Helpful for audits, not a user-facing control assistant layer |
| Git hygiene | Deferred | Repo maintenance, not assistant capability |
| CodeBuilder/BugFix/Refactor ideas | Parked | Developer automation would pull ATLAS away from the personal control assistant goal |

Developer-oriented automation must not become the default roadmap again unless explicitly approved in a later devtools track.

## New Roadmap

| Sprint | Focus |
|---|---|
| Sprint 36 | Product Realignment & Assistant Architecture |
| Sprint 37 | Action Architecture & Intent Schema - completed contract |
| Sprint 38 | PermissionManager & Action Approval Flow - completed decision engine |
| Sprint 39 | IntentRouter MVP - completed deterministic preview routing |
| Sprint 40 | PC Control Adapter MVP - completed |
| Sprint 41 | ConversationLoop MVP - completed |
| Sprint 42 | Personal Memory & Preferences - completed |
| Sprint 43 | RoutineEngine MVP - completed |
| Sprint 44 | Voice Core Architecture - completed |
| Sprint 45 | STT/TTS MVP - completed |
| Sprint 46 | DeviceRegistry + Room Model |
| Sprint 47 | Home Control Adapter Design |
| Sprint 48 | Desktop Tray / Permission Panel |
| Sprint 49 | Notification / Reminder / Calendar Assistant |
| Sprint 50 | End-to-End Personal Assistant Demo |
| Sprint 51 | Safety / Latency / UX Hardening |

## What Is Not Implemented Yet

- Voice layer
- Speech-to-text engine runtime
- Text-to-speech engine runtime
- Wake word runtime
- ActionRouter
- SkillRegistry
- Permission UI
- Home control adapter
- Device registry
- Desktop tray or dashboard
- Always-listening opt-in model
- Mobile companion bridge

## Next Sprint

Sprint 46 should be **DeviceRegistry + Room Model**. It should define canonical devices, aliases, rooms, and capability boundaries before any real home control runtime is introduced.

## Repo

https://github.com/Krayirhan/ATLAS
