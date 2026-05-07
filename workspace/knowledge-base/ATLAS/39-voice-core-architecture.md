# Sprint 44 - Voice Core Architecture

## Purpose

Sprint 44 defines the Voice Core Architecture for ATLAS. This sprint does not implement STT, TTS, microphone capture, wake word detection, or always-listening behavior. It prepares the contracts, safety rules, privacy boundaries, and selection criteria needed for Sprint 45.

## Architecture Stance

- local-first by default
- push-to-talk first
- wake word later
- no audio retention by default
- no separate voice execution path
- text pipeline remains canonical

## Voice Pipeline Diagram

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

## Push-to-Talk Flow

1. user manually starts capture
2. short command audio is captured
3. STT adapter returns transcript
4. transcript confidence is checked
5. low confidence returns clarification
6. transcript is routed through normal text-first assistant flow
7. response text may be spoken through TTS if available later

## STT Adapter Contract

### Models

`SpeechInput`

- `source`
- `audio_format`
- `language`
- `duration_ms`
- `metadata`

`TranscriptSegment`

- `start_ms`
- `end_ms`
- `text`
- `confidence`

`TranscriptResult`

- `text`
- `language`
- `confidence`
- `segments`
- `is_final`
- `warnings`
- `error_code`
- `metadata`

### Interface

`STTAdapter`

- `transcribe(input) -> TranscriptResult`
- `health_check()`
- `supported_languages()`
- `estimated_latency()`

## TTS Adapter Contract

### Models

`TTSRequest`

- `text`
- `language`
- `voice`
- `speed`
- `emotion_style` optional
- `metadata`

`TTSResult`

- `audio_output`
- `duration_ms`
- `engine`
- `success`
- `warnings`
- `error_code`
- `metadata`

### Interface

`TTSAdapter`

- `synthesize(request) -> TTSResult`
- `speak(request) -> TTSResult`
- `health_check()`
- `supported_voices()`
- `estimated_latency()`

## Wake Word Later Strategy

Wake word is not part of Sprint 44 or Sprint 45.

Prerequisites:

- push-to-talk MVP must be stable
- voice confirmation policy must be stable
- microphone activity indicator must exist
- false-positive test set must exist
- explicit opt-in must exist
- local wake engine must be preferred
- always-listening privacy policy must be finalized

## Voice Command Safety Model

Voice input is less trustworthy than text input because the recognition layer can be wrong before intent parsing even begins.

Core rules:

- transcript confidence gates the pipeline
- medium/high actions require explicit confirmation
- high-risk actions require transcript repeat-back
- ambiguous targets require clarification
- blocked actions remain blocked
- preview must precede any future execution

## Voice Confirmation Matrix

| Risk | Voice behavior |
|---|---|
| `safe_readonly` | reply if confidence is sufficient |
| `low` | preview first; optional confirmation when confidence is weak |
| `medium` | explicit confirmation required |
| `high` | explicit confirmation + repeated summary + strong warning |
| `blocked` | refusal |
| `ambiguous` | clarification |
| `unknown` | no action |

## Latency Budget

| Stage | Target |
|---|---|
| Push-to-talk start | `< 300 ms` |
| Short-command STT | `< 2-4 s` |
| Intent + permission decision | `< 500 ms` |
| Short-response TTS | `< 1-2 s` |
| Warm end-to-end | `< 5-7 s` |

Cold-load behavior must be measured separately for:

- STT model load
- Ollama warm/cold path
- TTS engine initialization

## Privacy and Security Boundaries

- no raw audio retention by default
- no cloud STT by default
- no cloud TTS by default
- no always-listening by default
- no automatic transcript-to-memory write
- sensitive transcript content must not be stored automatically
- delete-voice-history capability is a future requirement if voice history is ever introduced

## STT Option Comparison

| Option | Local | Turkish | Speed | Privacy | Windows | Assessment |
|---|---|---|---|---|---|---|
| `faster-whisper` | yes | strong candidate | strong | strong | good | preferred primary candidate |
| `whisper.cpp` | yes | strong candidate | strong | strong | good | preferred fallback / alternative |
| `Vosk` | yes | weaker | fast | strong | acceptable | lightweight fallback only |
| Windows Speech Recognition | partial | uncertain | good | mixed | strong | research-only |

## TTS Option Comparison

| Option | Local | Turkish | Speed | Privacy | Windows | Assessment |
|---|---|---|---|---|---|---|
| `Piper` | yes | promising | good | strong | good | preferred primary candidate |
| Windows built-in TTS | yes | depends on installed voices | good | strong | strong | preferred fallback |
| `Edge TTS` | no by default | natural | good | weaker | good | opt-in only, not default |

## Turkish Support Considerations

- app names can be pronounced inconsistently
- room/device aliases may use colloquial Turkish
- short confirmations like `evet` are dangerous for high risk
- volume/temperature numerals need explicit validation
- cancellation phrases need dedicated testing

## Failure Modes

| Failure | Risk | Mitigation |
|---|---|---|
| STT misrecognition | wrong command | confidence gating + clarification |
| low transcript confidence | unsafe routing | no action candidate |
| background noise | wrong target | push-to-talk + repeat-back |
| language mismatch | parse errors | explicit Turkish default + fallback |
| microphone unavailable | no voice path | text fallback |
| TTS unavailable | silent response | text fallback |
| false-positive wake word later | accidental activation | wake word deferred |
| command-injection-like speech | unsafe transcript | blocked phrase handling |
| preview mistaken for execution | trust issue | explicit preview-only copy |
| assistant claims success incorrectly | false state | forbid execution wording without runtime |

## Test Strategy

Sprint 44 test strategy is documentation-driven:

- validate architecture docs are aligned
- keep existing runtime tests green
- define Sprint 45 Turkish command set
- define STT/TTS health-check expectations before runtime implementation

## Acceptance Criteria

- push-to-talk first is explicit
- wake word later is explicit
- STT and TTS contracts are defined
- voice confirmation matrix is defined
- latency budget exists
- privacy and retention rules exist
- failure modes and mitigations exist
- Sprint 45 dependency is clear

## Sprint 45 Dependency

Sprint 45 should implement **STT/TTS MVP** against these contracts without adding microphone persistence, wake word runtime, or voice-driven action execution.
