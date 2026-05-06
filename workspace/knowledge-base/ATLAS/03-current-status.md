# ATLAS - Current Status

## Release Baseline

- **Release:** V1 RC - GO for the existing local control plane.
- **Canonical root:** `E:\ATLAS`.
- **Assistant core:** `E:\ATLAS\assistant-core`.
- **Knowledge base:** `E:\ATLAS\workspace\knowledge-base\ATLAS`.
- **Product direction after Sprint 36:** local-first personal control assistant foundation.
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
- **ToolApprovalAgent:** preview-only approval foundation; future basis for PermissionManager.
- **SecurityAuditorAgent:** bounded security audit; future basis for PC/home/privacy safety review.
- **Tests / doctor / audit:** `pytest`, `doctor --full`, `config validate`, `project validate ATLAS`, `ai doctor`, and `audit v1-rc` are the core health signals.

Current AI safety boundary:

- no file-writing AI
- no terminal-running AI
- no MCP tool-calling AI
- no git automation
- no approval token production
- no full prompt logging

## B) Parked DevTools Layer

These modules remain available as support infrastructure, but they are no longer the main product roadmap:

- **CodeReviewerAgent:** parked read-only code review support.
- **DocumentationAgent:** supporting knowledge/documentation hygiene.
- **ReportAgent / report synthesis:** parked ops/devtools reporting support.
- **Existing developer roadmap:** IntegrationAgent, TestWriterAgent, BugFixAgent, CodeBuilderAgent, RefactorAgent, and Git Hygiene are parked or must be re-scoped before any continuation.

Parked does not mean deleted. It means these items must not drive the personal assistant roadmap.

## C) Missing Personal Assistant Layers

These are not implemented yet and are the focus of Sprint 37+:

- Voice layer
- Speech-to-text adapter
- Text-to-speech adapter
- Wake word listener
- ConversationLoop
- Intent schema
- Action schema
- IntentRouter
- ActionRouter
- SkillRegistry
- Permission UX / PermissionManager
- PC control adapter
- Routine engine
- Personal memory and preferences
- Device registry
- Room model
- Home control adapter
- Desktop tray / permission panel
- Notification / reminder / calendar assistant
- Mobile bridge

## Sprint 36 Status

Sprint 36 is a documentation and architecture sprint. It does not add Python logic, agent code, CLI commands, tests, voice runtime, PC control runtime, or home automation runtime.

Sprint 36 success means ATLAS is realigned around the personal control assistant target and the next roadmap starts with action/intent/permission architecture.
