# ATLAS - Current Status

## Release Baseline

- **Release:** V1 RC - GO for the existing local control plane.
- **Canonical root:** `E:\ATLAS`.
- **Assistant core:** `E:\ATLAS\assistant-core`.
- **Knowledge base:** `E:\ATLAS\workspace\knowledge-base\ATLAS`.
- **Product direction after Sprint 36:** local-first personal control assistant foundation.
- **Sprint 37 status:** completed intent/action schema contract; no runtime execution.
- **Sprint 38 status:** completed PermissionManager decision flow; no personal action execution.
- **Sprint 39 status:** completed IntentRouter MVP; user text to safe preview flow is available.
- **Sprint 40 status:** completed PC Control Adapter MVP; safe dry-run PC plan generation is available.
- **Sprint 41 status:** completed ConversationLoop MVP; text-first session state and response building are available.
- **Sprint 42 status:** completed Personal Memory MVP; explicit remember/forget/show flow is available.
- **Sprint 43 status:** completed RoutineEngine MVP; built-in routine preview, risk aggregation, and routine CLI are available.
- **Sprint 44 status:** completed Voice Core Architecture; push-to-talk-first voice direction, privacy boundaries, and STT/TTS selection guidance are defined.
- **Important boundary:** `D:\ATLAS` is not an operational root. BenimFormum is not part of this sprint.

## A) Completed Core

These modules are preserved as the core technical foundation:

- **Ollama provider:** local LLM provider under `app/ai`.
- **Mock provider:** deterministic fallback and tests.
- **AI service:** provider/context orchestration for read-only AI queries.
- **Context loader:** bounded source loading from registry, memory summaries, KB, and selected reports.
- **Prompt composer:** read-only safety prompt foundation.
- **MemoryAgent foundation:** bounded project snapshot; future basis for personal memory.
- **ProjectQAAgent foundation:** project QA; future basis for personal knowledge QA.
- **PlannerAgent foundation:** sprint planning today; future basis for routine/task planning.
- **MainAgent:** deterministic read-only coordinator; future assistant coordinator.
- **ToolApprovalAgent:** preview-only devtools command/tool approval foundation.
- **SecurityAuditorAgent:** bounded security audit; future basis for PC/home/privacy safety review.
- **Action schema foundation:** `app/actions` contains Sprint 37 enum/dataclass contracts.
- **PermissionManager foundation:** `app/actions` contains Sprint 38 preview, permission decision, confirm/deny/cancel, and audit metadata contracts.
- **IntentRouter foundation:** `app/actions/intent_router.py` parses text into `IntentResult`, `ActionCandidate`, and `PermissionDecision` preview output.
- **Tests / doctor / audit:** `pytest`, `doctor --full`, `config validate`, `project validate ATLAS`, `ai doctor`, and `audit v1-rc` are the core health signals.

Current AI safety boundary:

- no file-writing AI
- no terminal-running AI
- no MCP tool-calling AI
- no git automation
- no approval token production
- no full prompt logging
- no action adapter execution

## B) Parked DevTools Layer

These modules remain available as support infrastructure, but they are no longer the main product roadmap:

- **CodeReviewerAgent:** parked read-only code review support.
- **DocumentationAgent:** supporting knowledge/documentation hygiene.
- **ReportAgent / report synthesis:** parked ops/devtools reporting support.
- **Existing developer roadmap:** IntegrationAgent, TestWriterAgent, BugFixAgent, CodeBuilderAgent, RefactorAgent, and Git Hygiene are parked or must be re-scoped before any continuation.

Parked does not mean deleted. It means these items must not drive the personal assistant roadmap.

## C) Completed Personal Assistant Architecture Contracts

Sprint 37 completed the first canonical contract layer:

- Intent category list.
- `IntentResult` schema.
- `ActionCandidate` schema.
- Action source values.
- Action type list.
- Risk model: `safe_readonly`, `low`, `medium`, `high`, `blocked`.
- `ActionPreview` dry-run/preview contract.
- `ActionResult` status contract.
- `ClarificationRequest` model.
- Ambiguous intent fallback rules.
- 90 Turkish command examples in `32-intent-action-schema.md`.

These are schema and documentation artifacts. They do not execute actions.

Sprint 38 completed the first personal action permission layer:

- `PermissionDecision` model.
- `PermissionStatus` values: `safe_readonly`, `preview_allowed`, `confirmation_required`, `clarification_required`, `denied`, `blocked`, `cancelled`, `unknown`.
- `PermissionManager` decision engine.
- `ActionCandidate -> ActionPreview -> PermissionDecision` flow.
- confirm/deny/cancel result modeling.
- blocked action non-execution decision.
- ambiguous/unknown clarification decision.
- voice-source confidence and confirmation rules.
- audit metadata helper with `execution_attempted=false`.
- `tests/test_permission_manager.py`.

This is still non-executing. No adapter is called.

Sprint 39 completed the first deterministic routing layer:

- `IntentRouter` rule-based MVP.
- text -> `IntentResult`.
- `IntentResult` -> `ActionCandidate`.
- `IntentRouter.preview()` -> `ActionPreview` + `PermissionDecision`.
- blocked, ambiguous, and unknown fallback handling.
- CLI preview command: `python -m app.cli ai intent`.
- `tests/test_intent_router.py`.
- `tests/test_ai_intent_cli.py`.

This is still non-executing. No adapter, browser action, media action, or terminal action runs.

## D) Missing Personal Assistant Runtime Layers

These are not implemented yet and are the focus of Sprint 44+:

- ActionRouter runtime
- SkillRegistry
- Browser/media/file execution beyond safe preview
- Device registry
- Room model
- Home control adapter
- Voice runtime
- Speech-to-text runtime
- Text-to-speech runtime
- Wake word runtime
- Desktop tray / permission panel
- Permission UI
- Durable action audit log
- Durable routine scheduler / daemon
- Notification / reminder / calendar assistant
- Mobile bridge

## Sprint 36 Status

Sprint 36 was a documentation and architecture sprint. It did not add Python application logic, agent code, CLI commands, tests, voice runtime, PC control runtime, or home automation runtime.

Sprint 36 success means ATLAS is realigned around the personal control assistant target and the roadmap starts with action/intent/permission architecture.

## Sprint 37 Status

Sprint 37 is complete as a schema and documentation sprint.

Completed:

- `32-intent-action-schema.md` was added.
- `25-assistant-architecture.md`, `26-action-architecture.md`, and `27-permission-ux.md` now describe the intent/action/permission flow.
- `app/actions` defines schema-only models and enums.
- `tests/test_action_models.py` validates the model contract.

Not implemented:

- Real action execution.
- Adapter implementation.
- PC control.
- Home control.
- Voice runtime.
- ConversationLoop.

## Sprint 38 Status

Sprint 38 is complete as a permission decision and documentation sprint.

Completed:

- `app/actions/permission.py` adds `PermissionManager`.
- `app/actions/preview.py` builds `ActionPreview`.
- `app/actions/audit.py` builds audit metadata.
- `PermissionDecision` and `PermissionStatus` are part of the action contracts.
- `33-permission-manager-flow.md` documents the flow and ToolApprovalAgent distinction.
- `tests/test_permission_manager.py` validates risk-to-decision behavior.

Not implemented:

- Personal action execution.
- PC/home adapter.
- Voice runtime.
- ConversationLoop.
- Permission UI.
- Durable runtime action audit log beyond metadata contract.

## Sprint 39 Status

Sprint 39 is complete as a deterministic routing and preview sprint.

Completed:

- `app/actions/intent_router.py` adds rule-based routing.
- `ai intent` CLI command previews route, candidate, and permission decision.
- user text -> `IntentResult` -> `ActionCandidate` -> `PermissionDecision` flow is available.
- ambiguous/unknown/blocked inputs stay on safe preview paths.

Not implemented:

- Personal action execution.
- Adapter implementation.
- PC/home control runtime.
- Voice runtime.
- ActionRouter runtime.

## Sprint 40 Status

Sprint 40 is complete as a safe PC preview planning sprint.

Completed:

- `app/control` defines preview-only PC plans and results.
- `ai pc-preview` CLI is available.
- Approved low/safe ATLAS actions can be translated into dry-run PC plans.

Not implemented:

- Real PC action execution.
- Shell or PowerShell executor.
- Destructive system actions.

## Sprint 41 Status

Sprint 41 is complete as a text-first conversation sprint.

Completed:

- `app/conversation` defines session state, response types, and response building.
- `ai chat` CLI is available.
- Intent preview, permission response, and PC dry-run planning are combined into a single conversation response flow.

Not implemented:

- Voice runtime.
- Background agent loop.
- Durable session storage.

## Sprint 42 Status

Sprint 42 is complete as a privacy-first personal memory sprint.

Completed:

- `app/personal_memory` defines in-memory memory items, policy, parsing, and service logic.
- `ai memory-personal` CLI is available.
- Explicit remember, forget, and show flows are covered by tests.

Not implemented:

- Durable memory storage.
- Sync or export runtime.
- Automatic passive memory capture.

## Sprint 43 Status

Sprint 43 is complete as a routine preview sprint.

Completed:

- `app/routines` defines `RoutineDefinition`, `RoutineStep`, `RoutinePreview`, and `RoutineResult`.
- Built-in routines exist for `calisma modu`, `oyun modu`, `uyku modu`, `toplanti modu`, `eve geldim`, and `evden cikiyorum`.
- Each routine step is evaluated through `PermissionManager`.
- `ai routine` CLI is available.
- `ConversationLoop` can answer routine requests through preview-only responses.
- Optional read-only PersonalMemory preference lookup can override generic app targets.

Not implemented:

- Real routine execution.
- Scheduler / daemon.
- Home or PC runtime execution from routine steps.
- Routine writes back into personal memory.

## Sprint 44 Status

Sprint 44 is complete as a voice architecture and safety sprint.

Completed:

- `28-voice-architecture.md` defines the canonical voice stance.
- `39-voice-core-architecture.md` defines the Voice Core Architecture in detail.
- push-to-talk first is the accepted MVP direction.
- wake word is explicitly deferred.
- STT and TTS adapter contracts are documented.
- voice-source safety rules and confirmation matrix are documented.
- latency targets, Turkish quality goals, and privacy boundaries are documented.

Not implemented:

- microphone capture runtime
- STT runtime
- TTS runtime
- wake word runtime
- always-listening mode
- voice-driven PC or home execution
- audio retention system

## Next Sprint

Sprint 45 should be **STT/TTS MVP**. It should implement contract-level local-first speech adapters around push-to-talk, keep wake word disabled, and preserve preview-only safety guarantees.
