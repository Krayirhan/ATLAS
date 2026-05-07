# Sprint 45 - STT/TTS MVP

## Purpose

Sprint 45 adds the first safe runtime slice for ATLAS voice support. The goal is not real speech control. The goal is a local-first, push-to-talk-compatible, mock-backed voice pipeline that exercises transcript safety, ConversationLoop integration, and mock TTS output without opening risky execution paths.

## Sprint Boundary

This sprint includes:

- `app/voice` package
- voice models
- STT/TTS adapter contracts
- mock STT
- mock TTS
- transcript -> `ConversationLoop` -> response -> mock TTS flow
- `ai voice` CLI

This sprint does not include:

- microphone capture
- raw audio retention
- wake word
- always-listening
- real STT engines
- real TTS engines
- voice-driven PC/home execution

## Mock STT/TTS

`MockSTTAdapter`

- accepts `mock_transcript`
- returns `TranscriptResult`
- does not read audio files
- does not use microphone

`MockTTSAdapter`

- accepts response text
- returns `TTSResult`
- does not generate audio files
- does not play real sound

## Optional Local Adapter Strategy

Sprint 45 may include local adapter stubs only:

- `FasterWhisperSTTAdapter`
- `PiperTTSAdapter`
- `WindowsTTSAdapter`

Rules:

- no required third-party dependency
- no model download
- no import-time hard failure
- `health_check()` returns unavailable if not implemented

## Push-to-Talk Only

The MVP remains push-to-talk only in architecture and runtime assumptions.

- no background listener
- no passive voice activation
- no microphone daemon

## Canonical Flow

```text
mock transcript / future push-to-talk
  -> MockSTTAdapter
  -> TranscriptResult
  -> voice policy
  -> ConversationLoop (source=voice)
  -> response
  -> MockTTSAdapter
  -> VoicePipelineResult
```

## CLI Examples

```powershell
python -m app.cli ai voice --project ATLAS --mock-transcript "Chrome'u ac"
python -m app.cli ai voice --project ATLAS --mock-transcript "Salon isigini ac" --show-safety
python -m app.cli ai voice --project ATLAS --mock-transcript "Sifrelerimi oku" --json
python -m app.cli ai voice --project ATLAS --mock-transcript "Isigi ac" --show-transcript
python -m app.cli ai voice --project ATLAS --mock-transcript "Calisma modunu baslat" --speak
```

## Safety Rules

- transcript confidence below threshold does not create a normal action flow
- blocked requests remain blocked
- ambiguous requests remain clarification-only
- medium/high voice requests remain confirmation-only
- execution_attempted is always false

## Privacy Rules

- audio_retained is always false
- microphone_used is always false
- wake_word_used is always false
- no audio file is written
- no transcript is written to memory automatically

## Test Plan

Validation coverage:

- voice models can be constructed
- mock adapters behave safely
- low-confidence transcript triggers clarification
- blocked/ambiguous/confirmation/action-preview voice paths work
- CLI JSON and text output work
- existing text/routine/memory/intent/pc-preview flows remain green

## Acceptance Criteria

- `app/voice` package exists
- mock STT/TTS exist
- `VoicePipeline` exists
- `ai voice` CLI exists
- `audio_retained=false`
- `microphone_used=false`
- `wake_word_used=false`
- `execution_attempted=false`
- no wake word runtime
- no always-listening
- no PC/home execution

## Next Dependency

Sprint 46 should define **DeviceRegistry + Room Model** before any real home/device runtime is introduced.
