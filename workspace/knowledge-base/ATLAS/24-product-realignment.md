# Sprint 36 - Product Realignment

## Problem Statement

ATLAS has a strong local control-plane and read-only AI foundation, but the roadmap drifted toward developer tooling. The main product goal is not a developer assistant. The main goal is a local-first personal control assistant for Windows that can understand text and future voice commands, then safely manage PC actions, personal knowledge, routines, and later device/home automation.

## Why Realignment Is Needed

The current foundation is valuable, but the next planned items were pulling ATLAS toward code review, report generation, code writing, bug fixing, refactoring, and Git hygiene. Those are useful maintenance tools, but they do not produce the user-facing assistant experience:

- voice/text command
- intent understanding
- action preview
- permission and confirmation
- safe PC control
- personal memory
- routines
- device/home control

Without realignment, ATLAS would keep improving repo-support tooling while the personal assistant product remains missing.

## What Went Wrong

1. The original master plan described a developer AI control plane.
2. Sprint 31 introduced CodeReviewerAgent as a first-class roadmap item.
3. Sprint 35 DocumentationAgent and ReportAgent-style work reinforced docs/reports as product momentum.
4. `06-next-sprints.md` pointed to IntegrationAgent, TestWriterAgent, BugFixAgent, CodeBuilderAgent, RefactorAgent, Git Hygiene, and tool execution approval.
5. Voice, intent, action, permission UX, PC control, routines, personal memory, device registry, and home control were not yet represented as the main roadmap.

## What Remains Valuable

| Existing part | Why it remains valuable |
|---|---|
| CLI core | Stable local control plane and validation entrypoint |
| Config loader | Local-first settings foundation |
| Project registry | Can later inspire user/device/profile registries |
| Safety policy | Core risk and blocked-source guard |
| Ollama provider | Local LLM runtime |
| Mock provider | Deterministic testing path |
| Context loader | Bounded source contract |
| Prompt composer | Safe reasoning prompt foundation |
| AI service | Provider/context orchestration |
| MemoryAgent | Foundation for personal memory |
| ProjectQAAgent | Foundation for personal knowledge QA |
| PlannerAgent | Foundation for routine/task planning |
| MainAgent | Future assistant coordinator |
| ToolApprovalAgent | Foundation for PermissionManager |
| SecurityAuditorAgent | Foundation for PC/home/privacy safety audit |
| Tests/doctor/audit | Quality gates for future assistant layers |

## What Is Parked

The following are preserved but removed from the main product path:

- CodeReviewerAgent
- DocumentationAgent as project documentation audit
- ReportAgent/report expansion
- generic IntegrationAgent
- TestWriterAgent
- BugFixAgent
- CodeBuilderAgent
- RefactorAgent
- Git Hygiene
- autonomous coding
- developer-only RAG/vector index

Parked means the code or idea is not deleted, but it must not define Sprint 37+.

## New Product Target

ATLAS is a local-first Windows personal control assistant foundation.

Target capabilities:

- understand text commands first
- support push-to-talk voice later
- use Ollama locally
- convert user intent into structured actions
- preview and classify action risk
- ask for approval when needed
- execute only safe approved actions
- audit all action decisions and results
- manage PC control first
- add personal memory and routines
- add home/device control later

## New Roadmap

| Sprint | Focus |
|---|---|
| 36 | Product Realignment & Assistant Architecture |
| 37 | Action Architecture & Intent Schema |
| 38 | PermissionManager & Action Approval Flow |
| 39 | IntentRouter MVP |
| 40 | PC Control Adapter MVP |
| 41 | ConversationLoop MVP |
| 42 | Personal Memory & Preferences |
| 43 | RoutineEngine MVP |
| 44 | Voice Core Architecture |
| 45 | STT/TTS MVP |
| 46 | DeviceRegistry + Room Model |
| 47 | Home Control Adapter Design |
| 48 | Desktop Tray / Permission Panel |
| 49 | Notification / Reminder / Calendar Assistant |
| 50 | End-to-End Personal Assistant Demo |
| 51 | Safety / Latency / UX Hardening |

## Decision Log

| Decision | Status | Rationale |
|---|---|---|
| ATLAS name remains ATLAS | Accepted | Product identity stays stable |
| Main goal is personal control assistant | Accepted | Corrects developer-tooling drift |
| Developer agents are parked | Accepted | Keeps value without driving product direction |
| Text-first, push-to-talk later | Accepted | Reduces voice privacy and STT risk |
| Wake word deferred | Accepted | Always-listening risk needs privacy design |
| PC control before home control | Accepted | Local, bounded, and easier to test |
| Home control requires DeviceRegistry and PermissionManager | Accepted | Prevents wrong-device and unsafe physical actions |
| No code changes in Sprint 36 | Accepted | This sprint is architecture and documentation only |

## Acceptance Criteria

- README presents the new product vision.
- `assistant-core/README.md` explains current and future technical layers.
- `00-master-plan.md` is converted to the new master plan.
- `03-current-status.md` separates completed core, parked devtools, and missing personal assistant layers.
- `06-next-sprints.md` contains Sprint 37-51 personal assistant roadmap.
- Architecture docs 25-31 exist.
- No Python application logic is changed by Sprint 36.
- Validation commands pass or failures are documented as conditional.

## Next Actions

1. Start Sprint 37 with Action Architecture & Intent Schema.
2. Define canonical `ActionSchema`.
3. Define initial action types and risk levels.
4. Define ambiguous intent fallback.
5. Keep PC control and voice implementation out of Sprint 37 until action/permission contracts are stable.
