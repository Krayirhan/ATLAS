# ATLAS Assistant Architecture

## Purpose

This document defines the target runtime architecture for ATLAS as a local-first personal control assistant.

## Canonical Flow

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

## Layer Responsibilities

| Layer | Responsibility | First implementation stance |
|---|---|---|
| Interaction Layer | Text, push-to-talk voice, future wake word, future desktop/mobile UI | Text first |
| AI Reasoning Layer | Ollama-backed interpretation and response | Existing `app/ai` foundation |
| Memory Layer | Preferences, routines, device aliases, safe history | Future personal memory |
| Intent/Action Layer | Intent schema, action schema, ActionRouter, SkillRegistry | Sprint 37+ |
| Permission Layer | Risk, preview, confirmation, blocked actions | Build on `app/approval` |
| Adapter Layer | PC, browser, media, files, future home | PC first |
| Audit Layer | Decision and result trail | Existing audit foundation |
| UI Layer | Permission panel, status, logs, settings | Later desktop tray/panel |

## Component Model

### User Input

Input may come from:

- CLI/text command
- future push-to-talk voice
- future desktop chat panel
- future mobile bridge

Wake word is deferred.

### ConversationLoop

Responsibilities:

- keep current interaction state
- handle cancel/interruption
- separate confirmation turns from new commands
- pass final user request to IntentRouter
- return response to text, TTS, or UI

### IntentRouter

Responsibilities:

- identify user intent
- classify ambiguity
- assign confidence
- avoid action routing when confidence is low
- preserve raw user goal for audit

### MainAgent

Current MainAgent coordinates read-only sub-agents. In the target architecture it becomes the assistant coordinator between intent reasoning and action planning.

Responsibilities:

- combine memory, context, policy, and routing signals
- choose whether the request is answer-only, plan-only, or action-candidate
- never execute directly

### CommandUnderstandingAgent

Future responsibility:

- normalize user phrasing
- extract target, parameters, constraints, and expected result
- identify missing information
- ask clarification if needed

### ActionRouter

Responsibilities:

- map structured intent to an action candidate
- choose adapter type
- validate action schema
- route unsupported actions to safe fallback

### PermissionManager

Responsibilities:

- classify risk
- decide preview/confirm/block
- enforce confirmation requirements
- handle timeout/cancel
- attach audit metadata

### Adapter

Adapters execute approved actions only.

Initial adapter priority:

1. PC control adapter.
2. Browser/media/file preview adapters.
3. Routine engine adapter.
4. Device/home adapter later.

### Result/Audit

Every action should produce:

- action id
- action type
- target
- risk level
- approval decision
- execution status
- result summary
- error or warning
- timestamp
- source channel

### TTS/UI Response

The assistant response must be clear:

- what was understood
- what was previewed
- what was approved/blocked
- what happened
- what the user can do next

## Non-Execution Rule

Reasoning layers do not execute. Only adapters execute, and only after PermissionManager approves or confirms the action.

## Security Boundary

The target architecture must preserve current boundaries:

- no full disk access
- no secret source reading
- no unrestricted terminal
- no autonomous coding path
- no home/device write action before permission and registry are ready
