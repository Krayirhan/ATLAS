# assistant-core

`assistant-core` is the Python CLI and local assistant foundation for ATLAS. It currently contains the healthy V1 control plane, read-only AI/agent core, Sprint 37 action contracts, Sprint 38 permission decision flow, Sprint 39 deterministic intent routing, Sprint 40 PC preview planning, Sprint 41 conversation loop MVP, Sprint 42 personal memory MVP, Sprint 43 routine preview MVP, Sprint 44 voice architecture decisions, Sprint 45 mock STT/TTS voice pipeline MVP, and Sprint 46 device registry plus room-model target resolution. Its technical direction is aligned around a personal control assistant, not a developer-agent product.

Sprint 37 added model/enumeration contracts. Sprint 38 added permission preview and decision logic. Sprint 39 added deterministic text-to-intent preview routing. Sprint 40 added safe PC dry-run planning. Sprint 41 added a text-first conversation loop. Sprint 42 added privacy-first personal memory. Sprint 43 added preview-only routines. Sprint 44 added the voice architecture and safety contracts. Sprint 45 added a mock-only voice package and CLI. Sprint 46 added an in-memory device registry, room model, alias resolution, and preview-only device planning. It still does not add microphone runtime, real STT/TTS engines, wake word runtime, home control runtime, or unrestricted command execution.

## Current Technical Foundation

| Area | Current status | Role in the new direction |
|---|---|---|
| `app/ai` | Implemented | Local LLM runtime, Ollama provider, mock provider, bounded context, prompt composition |
| `app/agents` | Implemented read-only agents | Existing reasoning/orchestration foundation |
| `app/approval` | Implemented preview-only devtools approval foundation | Command/file/tool preview for devtools support |
| `app/actions` | Implemented schema, permission, and router contracts | Intent/action/risk/preview/permission/router/result model foundation |
| `app/voice` | Implemented mock-only voice contracts and pipeline | Mock STT/TTS, transcript safety, no microphone runtime |
| `app/devices` | Implemented registry/resolver/planner foundation | Device registry, room model, alias resolution, capability matrix, no home execution |
| `app/commands/ai.py` | Implemented CLI surface | Current AI doctor/ask/agent/routine/chat/voice commands |
| `app/cli.py` | Implemented Typer app | Control plane and validation entrypoint |

## app/ai - Local LLM Runtime

`app/ai` is the local-first LLM runtime layer.

Current responsibilities:

- Ollama provider support.
- Mock provider for deterministic tests and fallback.
- Context loading from approved ATLAS sources.
- Prompt composition with read-only safety rules.
- `ai doctor`, `ai ask`, and `ai warmup` flows.

Future responsibilities:

- Support assistant intent prompts without broadening source access.
- Keep prompt logging metadata-only.
- Provide latency and warmup signals to future conversation UX.

## app/agents - Existing Read-Only Agents

Current agents are preserved, but their product roles are clarified:

| Agent | Current role | New product position |
|---|---|---|
| `MemoryAgent` | Project snapshot | Foundation for PersonalMemoryAgent |
| `ProjectQAAgent` | Project QA | Foundation for personal knowledge QA |
| `PlannerAgent` | Sprint plan | Reposition as routine/task planning foundation |
| `MainAgent` | Deterministic coordinator | Future assistant coordinator around intent/action routing |
| `ToolApprovalAgent` | Preview-only command approval | Devtools command/tool preview support |
| `SecurityAuditorAgent` | Bounded security audit | Future PC/home/privacy safety auditor |
| `CodeReviewerAgent` | Read-only code review | Parked devtools support |
| `DocumentationAgent` | Read-only docs audit | Supporting knowledge hygiene |
| `ReportAgent` | Read-only report synthesis | Parked ops/devtools support |

All existing agents must remain read-only until a later sprint explicitly designs execution boundaries.

## app/approval - DevTools Approval Foundation

`app/approval` currently models proposed commands, file changes, tool calls, approval status, risk, preview, requirements, and evaluator decisions.

Current role:

- ToolApprovalAgent support.
- Command/tool/git/MCP-style preview and block decisions.
- Devtools support subsystem, not the personal action runtime.
- No command execution.

## app/actions - Intent, Action, and Permission Contracts

Current Sprint 37/38/39 responsibility:

- `IntentResult`
- `ActionCandidate`
- `ActionPreview`
- `ActionResult`
- `ClarificationRequest`
- `PermissionDecision`
- `PermissionManager`
- `IntentRouter`
- `IntentPreviewResult`
- intent categories
- action types
- source values
- risk levels
- default risk mapping
- preview, confirmation, clarification, block, deny, cancel decisions
- deterministic rule-based text parsing
- entity extraction for MVP preview routes
- permission audit metadata with `execution_attempted=false`

No execution exists in `app/actions`.

Initial action types:

- `pc.open_app`
- `pc.open_folder`
- `pc.media.play_pause`
- `pc.system_info`
- `browser.search`
- `routine.run`
- `reminder.create`
- `device.turn_on`
- `device.turn_off`
- `device.set_brightness`

Future responsibility:

- `ActionRouter`
- `SkillRegistry`
- adapter handoff validation
- result and error model expansion

## app/voice

Sprint 45 adds the safe MVP package.

Current responsibility:

- mock STT transcript handling
- mock TTS response planning
- transcript safety policy
- transcript -> ConversationLoop -> response flow
- no audio retention
- no microphone runtime
- no wake word

Not implemented:

- microphone capture
- real STT runtime
- real TTS runtime
- wake word runtime

Wake word must not be implemented before the privacy model, voice confirmation policy, and opt-in behavior are documented and accepted.

## app/devices

Current responsibility:

- in-memory demo device registry
- canonical room model
- device alias and room alias resolution
- capability matrix
- device action preview planning
- conversation clarification support for ambiguous device targets

Not implemented:

- Home Assistant
- MQTT
- network discovery
- physical device control

## Future app/control

Planned responsibility:

- Windows PC control adapter.
- Browser/search adapter.
- Media adapter.
- File search preview adapter.
- Future home/device adapter integration boundary.

Initial PC actions must be safe, previewable, and reversible where possible. Destructive actions such as delete, shutdown, registry edits, installs, and admin commands remain blocked or deferred.

## app/routines

Current responsibility:

- built-in routine definitions
- routine preview
- routine result/audit metadata
- routine risk aggregation
- step-level PermissionManager decisions
- optional read-only personal preference lookup

Built-in routines:

- calisma modu
- oyun modu
- uyku modu
- toplanti modu
- evden cikiyorum
- eve geldim

## Validation Commands

Run from `E:\ATLAS\assistant-core`:

```powershell
python -m pytest -q
python -m app.cli doctor --full
python -m app.cli config validate
python -m app.cli project validate ATLAS
python -m app.cli ai doctor
python -m app.cli ai docs-audit --project ATLAS --provider mock --scope all-light
python -m app.cli ai security-audit --project ATLAS --provider mock --scope all-light
python -m app.cli audit v1-rc
```

## Non-Goals for the Assistant Runtime

- Autonomous coding agents as a primary product.
- Unrestricted terminal execution.
- Git push automation.
- Production deployment automation.
- Full disk MCP access.
- Secret file reading.
- Personal action execution before PermissionManager and adapter boundaries are tested.
- Wake word without privacy and permission design.
- Home/device control before permission and device registry are ready.
