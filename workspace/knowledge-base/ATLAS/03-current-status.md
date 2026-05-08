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
- **Sprint 45 status:** completed STT/TTS MVP; mock voice pipeline and `ai voice` CLI are available.
- **Sprint 46 status:** completed DeviceRegistry + Room Model; in-memory registry, alias resolution, and `ai device` CLI are available.
- **Sprint 47 status:** completed Home Control Adapter Design; contract-level home planning, mock adapter, and `ai home-preview` CLI are available.
- **Sprint 48 status:** completed Desktop Tray / Permission Panel backend; pending queue, model-only decisions, and `ai panel` CLI are available.
- **Sprint 49 status:** completed Notification / Reminder / Calendar Assistant; `ReminderService`, `CalendarService`, notification preview, `ai reminder`, `ai calendar`, and ConversationLoop reminder/calendar support are available.
- **Sprint 50 status:** completed End-to-End Personal Assistant Demo; `app/demo` package, 14 built-in scenarios, `DemoRunner`, `ai demo` CLI, Markdown/JSON report generation, safety policy validation, and 56 new tests are available. Generated demo report artifacts are not committed.
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
- **PersonalAssistant foundation:** `app/personal_assistant` now provides local reminder models, calendar draft/query preview, notification copy preview, and safe local JSON persistence.
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
- Home control adapter execution
- Voice runtime
- real speech-to-text runtime
- real text-to-speech runtime
- Wake word runtime
- Desktop tray runtime
- Durable action audit log
- Durable routine scheduler / daemon
- Real OS notification delivery
- External calendar API integration
- Background reminder scheduler / daemon
- Mobile bridge
- Network discovery

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

## Sprint 45 Status

Sprint 45 is complete as a mock-only voice runtime sprint.

Completed:

- `app/voice` package exists.
- mock STT and mock TTS exist.
- `VoicePipeline` routes transcript -> `ConversationLoop` -> mock TTS.
- `ai voice` CLI is available.

Not implemented:

- microphone capture
- real STT/TTS engine runtime
- wake word
- always-listening

## Sprint 46 Status

Sprint 46 is complete as a device identity and target-resolution sprint.

Completed:

- `app/devices` defines device, room, alias, capability, state, resolution, and plan models.
- In-memory demo `DeviceRegistry` exists.
- `DeviceTargetResolver` resolves room/device aliases and returns clarification when target is ambiguous.
- `DeviceActionPlanner` produces preview-only device plans and never executes home actions.
- `ai device` CLI is available.
- `ConversationLoop` now returns better device clarification and confirmation responses.

Not implemented:

- real home control execution
- Home Assistant or MQTT integration
- network discovery
- physical device state changes
- durable device storage
- voice-driven PC or home execution
- audio retention system

## Sprint 47 Status

Sprint 47 is complete as a home preview contract sprint.

Completed:

- `app/home` defines `HomeControlAdapter`, `HomeControlPlan`, `HomeControlResult`, and state read/write request/result models.
- `MockHomeControlAdapter` exists and never performs real network or physical device execution.
- `HomeControlPlanner` maps `DeviceActionPlan` into preview-only home plans.
- `ai home-preview` CLI is available.
- Home Assistant is documented as the first real adapter candidate.
- MQTT is documented as an alternative, not a default.

Not implemented:

- real home execution
- Home Assistant client
- MQTT client
- network discovery
- token or credential loading
- physical device state changes
- durable home state sync

## Sprint 48 Status

Sprint 48 is complete as a permission visibility and queue sprint.

Completed:

- `app/panel` defines panel item, decision, state, and operation models.
- Pending confirmation queue exists through in-memory or safe local JSON store.
- `PermissionPanelService` can submit text through `ConversationLoop` and persist preview/block/clarification items.
- `ai panel` CLI can submit, list, show, approve, deny, cancel, and clear panel items.
- Approve updates model state only and does not start real execution.

Not implemented:

- desktop tray runtime
- GUI framework
- background tray daemon
- post-approval real execution
- notification badges or OS-level notifications

## Sprint 49 Status

Sprint 49 is complete as a local-first reminder/calendar/notification preview sprint.

Completed:

- `app/personal_assistant` defines reminder, calendar, notification, parser, policy, service, and store layers.
- `ReminderService` supports create, list, preview, and cancel over local-only state.
- `CalendarService` supports safe local query preview and local event drafts.
- notification preview copy exists through `NotificationService`.
- `ConversationLoop` now intercepts reminder/calendar requests before the generic router fallback.
- `PermissionPanelService` can queue reminder and calendar confirmation items.
- `ai reminder` and `ai calendar` CLIs are available.

Not implemented:

- real OS notification delivery
- background scheduler / daemon
- reminder firing runtime
- Google Calendar or Outlook integration
- external calendar write
- email or push notification delivery

## Next Sprint

Sprint 50 should be **End-to-End Personal Assistant Demo**. It should combine reminder/calendar preview, panel visibility, safe PC preview, routine preview, and mock voice flows into one coherent demo path.
