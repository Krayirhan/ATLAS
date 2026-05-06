# ATLAS Voice Architecture

## Purpose

This document defines the voice direction for ATLAS. It is architecture only. No voice runtime is implemented in Sprint 36.

## Stance

ATLAS uses push-to-talk first. Wake word comes later only after privacy, always-listening, confirmation, and microphone status UX are accepted.

## Voice Pipeline

```text
push-to-talk audio
  -> STT adapter
  -> text command
  -> ConversationLoop
  -> IntentRouter
  -> PermissionManager
  -> Adapter
  -> Result
  -> TTS/UI response
```

## Push-to-Talk First

Reasons:

- lower privacy risk
- clearer user intent
- easier debugging
- lower false activation risk
- simpler MVP acceptance criteria

## Wake Word Later

Wake word is deferred because it requires:

- clear microphone status indicator
- always-listening privacy policy
- local-first wake detection stance
- false positive mitigation
- household privacy decision
- confirmation policy for risky actions

## STT Options

Candidate categories:

- local/offline STT models
- hybrid local-first option if explicitly configured later
- Windows speech APIs if privacy and language quality fit

Selection criteria:

- Turkish command quality
- offline/local-first capability
- latency
- resource usage
- deterministic testability
- clear failure mode

## TTS Options

Candidate categories:

- local TTS engine
- Windows local voice output
- optional provider later if explicitly configured

Selection criteria:

- Turkish quality
- latency
- understandable short confirmations
- offline/local-first behavior
- ability to interrupt/cancel speech

## Turkish Support

Voice MVP must include a Turkish command test set:

- open app commands
- open folder commands
- system info commands
- media commands
- routine commands
- cancellation commands
- confirmation commands

Target for early MVP: high accuracy for simple commands before any medium/high risk voice action is allowed.

## Latency Targets

Initial targets:

- push-to-talk audio capture start: immediate
- STT for short command: under 2 seconds target
- warm Ollama action interpretation: under 5 seconds target
- TTS short response: under 2 seconds target

Cold Ollama starts require visible status messaging.

## Privacy Rules

- No always-listening until wake word privacy design is accepted.
- No raw microphone recording saved by default.
- No cloud STT by default.
- No voice-derived sensitive data stored in personal memory unless explicitly approved.
- Text fallback always exists.

## Cancellation and Interrupt

Voice loop must support:

- cancel pending action
- stop speaking
- interrupt TTS
- expire pending confirmation
- ask clarification when target is ambiguous

## Fallback to Text

If STT fails, confidence is low, or latency is too high, ATLAS must return to text interaction. Text remains the reliable baseline.
