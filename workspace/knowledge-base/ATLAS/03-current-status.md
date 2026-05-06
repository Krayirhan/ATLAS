# ATLAS - Current Status

## Release Baseline

- **Release:** V1 RC - GO for the existing local control plane.
- **Canonical root:** `E:\ATLAS`.
- **Assistant core:** `E:\ATLAS\assistant-core`.
- **Knowledge base:** `E:\ATLAS\workspace\knowledge-base\ATLAS`.
- **Product direction after Sprint 36:** local-first personal control assistant foundation.
- **Sprint 37 status:** completed intent/action schema contract; no runtime execution.
- **Sprint 38 status:** completed PermissionManager decision flow; no personal action execution.
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

## D) Missing Personal Assistant Runtime Layers

These are not implemented yet and are the focus of Sprint 39+:

- IntentRouter runtime
- ActionRouter runtime
- SkillRegistry
- PC control adapter
- Browser/media/file adapter execution
- Routine engine
- Personal memory and preferences runtime
- Device registry
- Room model
- Home control adapter
- Voice layer
- Speech-to-text adapter
- Text-to-speech adapter
- Wake word listener
- ConversationLoop
- Desktop tray / permission panel
- Permission UI
- Durable action audit log
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

## Next Sprint

Sprint 39 should be **IntentRouter MVP**. It should convert user text into `IntentResult` and safe `ActionCandidate` objects that can be passed through PermissionManager.
