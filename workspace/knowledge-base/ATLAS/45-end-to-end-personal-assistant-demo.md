# Sprint 50 - End-to-End Personal Assistant Demo

## Purpose

Sprint 50 combines all preview-only assistant layers into a single demonstrable flow. Sprint 51 keeps this demo intact and hardens its safety, latency, and UX behavior.

## Demo Surfaces

- chat / PC preview
- device clarification and planning
- home preview
- routine preview
- memory preview / blocked memory
- reminder draft
- calendar draft / query preview
- panel queue
- mock voice preview

## Demo Safety Boundary

Every scenario must keep these flags false:

- `execution_attempted`
- `physical_device_touched`
- `network_used`
- `microphone_used`
- `wake_word_used`
- `audio_retained`
- `external_calendar_used`
- `os_notification_sent`
- `credential_accessed`
- `shell_used`

Sprint 51 tightens demo validation so missing safety flags also fail the scenario.

## Commands

```powershell
python -m app.cli ai demo --project ATLAS --all --show-safety
python -m app.cli ai demo --project ATLAS --all --json
python -m app.cli ai demo --project ATLAS --all --markdown --no-write
python -m app.cli ai hardening --project ATLAS --all --markdown --no-write
```

## Preview vs Execution

The demo must never imply real execution:

- Chrome does not really open
- home devices do not really change
- reminders are drafts only
- calendar events are drafts only
- voice is mock-only
- approval does not execute

## Artifact Policy

- demo Markdown goes under `workspace/outputs/demo/`
- hardening Markdown goes under `workspace/outputs/hardening/`
- generated reports stay local artifacts and should not be newly committed

## Sprint 51 Link

See `46-safety-latency-ux-hardening.md` for the hardening layer that now sits on top of the demo.
