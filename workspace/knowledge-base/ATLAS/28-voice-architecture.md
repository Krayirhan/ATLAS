# ATLAS Voice Architecture

## Purpose

This document defines the voice direction for ATLAS after Sprint 44. It is architecture and policy only. No microphone runtime, STT engine, TTS engine, wake word engine, or audio retention flow is implemented here.

## Voice Layer Goal

ATLAS should eventually accept short spoken commands, convert them into safe text-like requests, apply the same intent and permission controls already used by the text pipeline, and optionally speak back a response.

Voice is not a separate authority path. It is an input/output layer around the existing text-first assistant core.

## Text-First Core Relationship

The current assistant core remains text-first:

- `ConversationLoop` owns interaction state
- `IntentRouter` produces structured intent
- `PermissionManager` decides preview / clarification / confirmation / block
- `ResponseBuilder` produces the assistant message

Voice must wrap this core, not bypass it.

## Push-to-Talk First

Sprint 45 MVP must start with push-to-talk.

Reasons:

- lower privacy risk
- no false wake-word activation
- clearer user intent boundary
- easier latency measurement
- easier testability on Windows
- lower chance of accidental risky action preview

## Wake Word Later

Wake word is explicitly deferred.

Wake word cannot be enabled until:

- push-to-talk MVP is stable
- voice confirmation rules are validated
- microphone status indicator exists
- false-positive tests exist
- always-listening privacy policy is accepted
- local-first wake engine candidate is selected
- opt-in enablement exists

## Canonical Voice Pipeline

```text
Push-to-talk input
  -> Audio capture
  -> STT adapter
  -> Transcript
  -> Transcript confidence check
  -> ConversationLoop
  -> IntentRouter
  -> PermissionManager
  -> ActionPreview / RoutinePreview / MemoryOperation
  -> ResponseBuilder
  -> TTS adapter
  -> User hears response
```

Sprint 44 only documents this flow. It does not implement it.

## STT Pipeline

Target stages:

1. user presses push-to-talk
2. short audio window is captured
3. STT adapter produces transcript
4. transcript confidence is evaluated
5. low confidence returns clarification
6. transcript is routed through the normal assistant pipeline

### STT Adapter Contract

`SpeechInput`

- `source`
- `audio_format`
- `language`
- `duration_ms`
- `metadata`

`TranscriptResult`

- `text`
- `language`
- `confidence`
- `segments`
- `is_final`
- `warnings`
- `error_code`
- `metadata`

`STTAdapter`

- `transcribe(input) -> TranscriptResult`
- `health_check()`
- `supported_languages()`
- `estimated_latency()`

### STT Options

| Option | Local-first | Turkish quality | Latency | Privacy | Windows fit | Notes |
|---|---|---|---|---|---|---|
| `faster-whisper` | Yes | strong candidate | good on GPU / acceptable on CPU | strong | good | best near-term default candidate if packaging is manageable |
| `whisper.cpp` | Yes | good | good on CPU for short commands | strong | good | simpler native distribution path, good fallback candidate |
| `Vosk` | Yes | mixed for modern Turkish command quality | fast | strong | acceptable | lightweight, but likely weaker command accuracy |
| Windows Speech Recognition | partly local | uncertain for Turkish assistant commands | good | depends on OS behavior | strong | keep as fallback research item, not primary MVP target |
| cloud STT later | No by default | varies | varies | weaker | varies | not default; only future opt-in |

Sprint 44 comparison result:

- first implementation candidates: `faster-whisper` and `whisper.cpp`
- `Vosk` stays as a lightweight fallback candidate
- Windows built-in STT is research-only, not default architecture
- cloud STT is explicitly out of default MVP scope

## TTS Pipeline

Target stages:

1. `ResponseBuilder` creates final user-facing text
2. TTS adapter receives short response text
3. TTS output is synthesized
4. speech may be interrupted or cancelled
5. if TTS fails, text output remains the fallback

### TTS Adapter Contract

`TTSRequest`

- `text`
- `language`
- `voice`
- `speed`
- `emotion/style` optional
- `metadata`

`TTSResult`

- `audio_output`
- `duration_ms`
- `engine`
- `success`
- `warnings`
- `error_code`
- `metadata`

`TTSAdapter`

- `synthesize(request) -> TTSResult`
- `speak(request) -> TTSResult`
- `health_check()`
- `supported_voices()`
- `estimated_latency()`

### TTS Options

| Option | Local-first | Turkish quality | Latency | Privacy | Windows fit | Notes |
|---|---|---|---|---|---|---|
| `Piper` | Yes | promising local baseline | good | strong | good | primary local-first candidate |
| `Edge TTS` | No by default | often high naturalness | good | weaker | good | keep only as opt-in later, not default |
| Windows SAPI / built-in TTS | local OS path | acceptable but depends on installed voices | good | strong | strong | viable fallback if Turkish voice quality is sufficient |
| Coqui-like local engines later | Yes | varies | varies | strong | mixed | research-only for now |

Sprint 44 comparison result:

- primary local candidate: `Piper`
- fallback candidate: Windows built-in TTS
- `Edge TTS` remains non-default because it breaks local-first privacy by default

## Voice Source Safety

Voice commands are treated more conservatively than text commands.

Rules:

- low transcript confidence -> no action candidate, clarification required
- ambiguous target -> clarification required
- blocked action -> blocked
- medium/high risk voice action -> explicit confirmation required
- high risk voice action -> repeat transcript summary before confirmation
- single-word confirmation such as `evet` is not enough for high risk by default
- preview must exist before any future execution path

## Voice Confirmation Policy

| Risk | Voice behavior |
|---|---|
| `safe_readonly` | answer allowed if transcript confidence is sufficient |
| `low` | preview first; lightweight confirmation may be used if confidence is weak |
| `medium` | explicit confirmation required |
| `high` | explicit confirmation + repeated summary + strong warning |
| `blocked` | refusal |
| `ambiguous` | clarification |
| `unknown` | no action |

High-risk confirmation copy must include:

- the interpreted action
- the concrete target
- the risk warning
- a clear cancel path

## Confidence Threshold Policy

Initial architecture stance:

- `>= 0.85`: normal voice preview path
- `0.70 - 0.84`: clarification preferred for risky or target-sensitive commands
- `< 0.70`: no action candidate; clarification only

These thresholds are architectural starting points and must be revalidated in Sprint 45 with Turkish command tests.

## Latency Targets

Target budgets for short spoken commands:

- push-to-talk recording start: `< 300 ms`
- STT short command: `< 2-4 s`
- intent + permission decision: `< 500 ms`
- TTS short reply: `< 1-2 s`
- warm end-to-end path: `< 5-7 s`

Cold-start notes:

- STT model cold load must be measured separately
- Ollama warmup remains a separate contributor
- ATLAS should expose warm/cold state in future UX

## Turkish Quality Targets

Early Turkish voice quality goals:

- simple PC/routine commands should be transcribed accurately
- room/device/app names need a dedicated Turkish command set
- confirmations and cancellations must be robust under short utterances
- background-noise degradation must be visible in logs/telemetry later

Sprint 45 should validate:

- app names
- routine names
- room names
- numbers such as volume and temperature
- cancellation phrases
- confirmation phrases

## Privacy Rules

- no always-listening by default
- no raw audio saved by default
- no cloud STT by default
- transcript is used only for the conversation pipeline
- memory writes still require explicit remember flow
- sensitive transcript content must not be stored automatically
- wake word requires explicit opt-in later

## Audio Data Retention Policy

Default policy:

- no audio file retention
- no raw microphone recording storage
- no silent background capture archive
- no transcript-to-memory write without explicit user request

Future requirement:

- user must be able to delete voice history if any voice history is later introduced

## Failure Modes

| Failure mode | Effect | Mitigation |
|---|---|---|
| STT misheard command | wrong transcript | clarification, repeat-back, confidence gating |
| low confidence transcript | unsafe action guess | no action; clarification only |
| background noise | corrupted target or command | push-to-talk, short capture window, confidence check |
| language mismatch | wrong parsing | force Turkish default and report mismatch |
| microphone unavailable | no voice input | text fallback |
| TTS unavailable | no spoken response | text fallback |
| slow model load | poor UX | warmup indicators, latency budget tracking |
| command-injection-like speech | unsafe literal transcript | same blocked-phrase and router safety rules as text |
| user thinks preview executed | trust failure | response copy must explicitly state preview-only |
| assistant claims execution incorrectly | false system state | keep execution wording forbidden until real runtime exists |

## No Always-Listening Until Explicit Approval

Always-listening is not part of Sprint 44 or Sprint 45.

It remains blocked until:

- opt-in exists
- privacy indicator exists
- wake word false-positive tests exist
- retention policy is finalized
- cancellation and confirmation runtime is stable

## Sprint 45 STT/TTS MVP Plan

Sprint 45 should:

1. choose one STT primary candidate and one fallback
2. choose one TTS primary candidate and one fallback
3. define Windows install/setup path
4. define Turkish command evaluation set
5. add contract-level health checks
6. keep execution boundary closed

Sprint 45 must still avoid:

- real PC execution from voice
- home execution from voice
- wake word runtime
- always-listening daemon
