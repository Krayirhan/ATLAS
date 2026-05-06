# ATLAS Assistant Architecture

## Purpose

This document defines the target runtime architecture for ATLAS as a local-first personal control assistant. Sprint 37 refines the architecture around canonical intent and action contracts, without adding real action execution.

## Sprint 37 Architecture Update

Sprint 36 established the personal control assistant direction. Sprint 37 defines the structured handoff between natural language understanding, action planning, risk classification, permission, adapter execution, and audit.

The key change is that natural language is no longer routed directly toward a tool or adapter. It must first become an `IntentResult`, then an `ActionCandidate`, then an `ActionPreview`, and only a future approved adapter may produce an `ActionResult`.

## Canonical Flow

```text
User Input
  -> ConversationLoop
  -> IntentRouter
  -> IntentResult
  -> ActionCandidate
  -> RiskClassifier
  -> PermissionManager
  -> ActionPreview
  -> Adapter
  -> ActionResult
  -> Audit + Response
```

## Layer Responsibilities

| Layer | Responsibility | Current status |
|---|---|---|
| Interaction Layer | Text input now; future push-to-talk voice, wake word, desktop panel, mobile bridge | Text/CLI foundation exists |
| Conversation Layer | Session state, cancellation, confirmation turns, stale action prevention | Not implemented |
| Intent Layer | Classify user request into `IntentResult`, confidence, entities, ambiguity | Schema defined in Sprint 37 |
| AI Reasoning Layer | Ollama-backed interpretation, bounded context, answer-only reasoning | Existing `app/ai` foundation |
| Main Coordination Layer | Decide whether request is answer, clarification, plan, or action candidate | Existing `MainAgent` foundation |
| Action Layer | Canonical `ActionCandidate`, action type, target, parameters, source, expected result | Schema defined in Sprint 37 |
| Risk Layer | Default risk, voice-source risk, target ambiguity, blocked categories | Schema defined in Sprint 37 |
| Permission Layer | Preview, confirmation, denial, block, timeout, cancel | Sprint 38 target |
| Adapter Layer | Execute approved PC, browser, media, routine, or future device actions | Not implemented |
| Audit Layer | Capture intent, action, risk, permission, result, timestamps | Contract defined; runtime pending |
| UI Layer | Permission panel, status, logs, settings, routine editor | Future desktop layer |

## Component Contracts

### User Input

Input may come from:

- CLI/text command.
- Future desktop chat panel.
- Future push-to-talk voice.
- Future mobile bridge.
- Future scheduled routine trigger.

Wake word is deferred until privacy, cancellation, and confirmation policies are implemented.

### ConversationLoop

Responsibilities:

- Keep the current interaction state.
- Separate a new command from a pending confirmation.
- Handle cancel and interruption.
- Expire stale confirmations.
- Pass a final user request to `IntentRouter`.
- Return text, future TTS, or UI response.

Sprint 37 does not implement `ConversationLoop`.

### IntentRouter

Responsibilities:

- Produce `IntentResult`.
- Classify category, confidence, language, raw text, normalized text, entities, and target.
- Detect `unknown`, `ambiguous`, and `blocked` intent.
- Avoid action creation when target or category is unclear.
- Preserve raw user goal for audit.

Sprint 39 implementation stance:

- deterministic and rule-based
- text-only MVP
- no LLM dependency
- no adapter calls
- no execution

Low confidence intent must not become an executable action. Ambiguous intent must produce a clarification request.

### IntentResult

Canonical fields:

- `intent_id`
- `category`
- `confidence`
- `language`
- `raw_text`
- `normalized_text`
- `entities`
- `target`
- `action_candidate`
- `ambiguity_reason`
- `requires_clarification`
- `safety_notes`

### MainAgent

Current `MainAgent` coordinates read-only sub-agents. In the target architecture it becomes the assistant coordinator between intent reasoning and action planning.

Responsibilities:

- Decide whether the user request is answer-only, memory query, clarification, or action-candidate.
- Use bounded context and policy.
- Avoid direct execution.
- Route developer-tool requests to parked/supporting devtools agents only when explicitly needed.

### CommandUnderstandingAgent

Future responsibility:

- Normalize phrasing.
- Extract target, parameters, constraints, and expected result.
- Identify missing information.
- Ask clarification before action creation.

This may remain a logical responsibility inside `IntentRouter` until a later sprint.

### ActionRouter

Responsibilities:

- Map structured intent to `ActionCandidate`.
- Select an action type from the canonical list.
- Validate target and parameters.
- Reject unsupported or blocked actions.
- Route supported actions to the future adapter family only after permission gates.

Sprint 37 defines the schema. Sprint 39 adds deterministic runtime preview routing without execution.

### ActionCandidate

Canonical fields:

- `action_id`
- `action_type`
- `target`
- `parameters`
- `source`
- `user_goal`
- `intent_category`
- `risk_level`
- `requires_confirmation`
- `dry_run_supported`
- `reversible`
- `expected_result`
- `blocked_reason`
- `confirmation_prompt`
- `audit_metadata`

### RiskClassifier

Responsibilities:

- Assign `safe_readonly`, `low`, `medium`, `high`, or `blocked`.
- Consider reversibility, physical-world impact, privacy, system changes, data loss, voice source, confidence, and target ambiguity.
- Force blocked actions to non-executable status.
- Require confirmation for medium/high actions.

### PermissionManager

Responsibilities:

- Convert an `ActionCandidate` into an `ActionPreview`.
- Decide whether confirmation is optional, required, or impossible.
- Enforce timeout and cancel.
- Prevent blocked actions from reaching adapters.
- Attach audit metadata.

Sprint 38 implements this flow. Sprint 37 only defines the contract.

### ActionPreview

Canonical fields:

- `action_id`
- `summary`
- `target`
- `parameters_preview`
- `risk_level`
- `will_change_state`
- `requires_confirmation`
- `reversible`
- `estimated_effect`
- `warnings`
- `safe_to_execute`
- `blocked_reason`

Medium/high actions cannot execute without preview. Blocked action preview only explains why execution is not allowed.

### Adapter

Adapters execute approved actions only. They do not interpret natural language and they do not override permission decisions.

Initial adapter priority:

1. PC control adapter.
2. Browser, media, and file-search preview adapters.
3. Routine engine adapter.
4. Device/home adapter later.

### ActionResult

Canonical fields:

- `action_id`
- `status`
- `executed`
- `dry_run`
- `message`
- `result_data`
- `error_code`
- `error_message`
- `audit_metadata`
- `started_at`
- `finished_at`

Status values:

- `planned`
- `previewed`
- `awaiting_confirmation`
- `approved`
- `denied`
- `blocked`
- `executed`
- `failed`
- `cancelled`
- `skipped`

Sprint 37 does not execute actions. `ActionResult` is a future runtime contract.

### Audit + Response

Every action path should eventually record:

- raw user goal
- normalized intent
- action type and target
- source channel
- confidence
- risk level
- permission decision
- adapter selected
- execution status
- timestamps
- warnings or errors

The user-facing response must state what was understood, what will change, whether confirmation is required, and what happened or why the action was blocked.

## Ambiguity and Clarification

Ambiguous intent does not create an executable action. It creates a clarification request with:

- reason
- missing fields
- candidate targets
- suggested questions
- safe default

Example:

```text
User: "Isigi ac"
Assistant: "Hangi isigi acmami istersin? Salon, calisma odasi veya yatak odasi?"
Safe default: no action
```

## Execution Boundary

Sprint 37 contains no real execution:

- No PC control adapter.
- No home control adapter.
- No voice runtime.
- No terminal executor.
- No file operation execution.
- No adapter implementation.
- No new CLI execution command.

The only allowed code surface is schema-level model and enum contracts.

## Security Boundary

The target architecture must preserve current boundaries:

- No full disk access.
- No secret source reading.
- No unrestricted terminal.
- No autonomous coding path.
- No direct adapter execution from natural language.
- No home/device write action before `PermissionManager` and `DeviceRegistry` are ready.

## Sprint Dependencies

| Sprint | Dependency |
|---|---|
| Sprint 38 | `PermissionManager` and action approval flow consume `ActionCandidate`, `RiskLevel`, and `ActionPreview` |
| Sprint 39 | `IntentRouter` produces `IntentResult` and action candidates |
| Sprint 40 | `PCControlAdapter` consumes approved actions only |
| Sprint 43 | `RoutineEngine` uses action preview and child-action risk aggregation |
| Sprint 47 | Home control waits for `DeviceRegistry`, room model, and permission enforcement |
