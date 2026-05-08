# ATLAS - Current Status

## Release Baseline

- **Release:** V1 RC - GO for preview-only assistant flows.
- **Canonical root:** `E:\ATLAS`
- **Assistant core:** `E:\ATLAS\assistant-core`
- **Knowledge base:** `E:\ATLAS\workspace\knowledge-base\ATLAS`
- **Product direction:** local-first personal control assistant foundation
- **MainAgent:** preserved read-only coordination foundation
- **ToolApprovalAgent:** preserved preview-only approval foundation
- **SecurityAuditorAgent:** preserved bounded read-only security audit foundation

## Sprint Status

- **Sprint 37:** Intent / Action schema completed
- **Sprint 38:** PermissionManager completed
- **Sprint 39:** IntentRouter MVP completed
- **Sprint 40:** PCControlAdapter preview MVP completed
- **Sprint 41:** ConversationLoop MVP completed
- **Sprint 42:** PersonalMemoryService completed
- **Sprint 43:** RoutineEngine MVP completed
- **Sprint 44:** Voice Core Architecture completed
- **Sprint 45:** Mock STT/TTS VoicePipeline completed
- **Sprint 46:** DeviceRegistry + Room Model completed
- **Sprint 47:** HomeControlAdapter mock preview completed
- **Sprint 48:** Permission Panel backend completed
- **Sprint 49:** Reminder / Calendar / Notification preview completed
- **Sprint 50:** End-to-End Personal Assistant Demo completed
- **Sprint 51:** Safety / Latency / UX Hardening completed

## Sprint 51 Outcome

Sprint 51 moves ATLAS from a showable preview demo to a harder V1 demo baseline.

Completed in Sprint 51:

- central safety invariant suite
- latency measurement and typed latency report
- `ai hardening` CLI
- confirmation timeout / cancel policy for panel items
- stricter voice confirmation wording and low-confidence clarification
- clearer Turkish preview UX copy
- docs cleanup for current status and hardening behavior
- generated artifact policy clarification

## Available User-Facing Preview Surfaces

- `ai chat`
- `ai voice`
- `ai pc-preview`
- `ai device`
- `ai home-preview`
- `ai routine`
- `ai reminder`
- `ai calendar`
- `ai notification-preview`
- `ai panel`
- `ai demo`
- `ai hardening`

## Current Safety Boundary

The following are still **not implemented**:

- real PC execution
- real home execution
- real scheduler / daemon
- real OS notification delivery
- real external calendar API
- real microphone capture
- wake word / always-listening
- shell / terminal executor
- credential or `.env` reading

Preview flows must keep these invariants false:

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

## Current Runtime Layers

- `app/actions`: schema, risk, permission, router contracts
- `app/conversation`: text-first conversation and response shaping
- `app/control`: PC preview plans only
- `app/devices`: room/device registry and preview planning
- `app/home`: mock home preview adapter
- `app/panel`: pending queue and non-executing approval state
- `app/personal_assistant`: reminder/calendar/notification preview flows
- `app/voice`: mock transcript pipeline
- `app/demo`: end-to-end preview demo
- `app/quality`: Sprint 51 safety and latency hardening

## Validation Signals

Run from `E:\ATLAS\assistant-core`:

```powershell
python -m pytest -q
python -m app.cli doctor --full
python -m app.cli config validate
python -m app.cli project validate ATLAS
python -m app.cli ai demo --project ATLAS --all --show-safety
python -m app.cli ai hardening --project ATLAS --all --markdown --no-write
python -m app.cli ai docs-audit --project ATLAS --provider mock --scope all-light
python -m app.cli ai security-audit --project ATLAS --provider mock --scope all-light
python -m app.cli audit v1-rc
```

## Next Sprint

Sprint 52 is **Safe Execution Gate / Low-Risk PC Execution Planning**.

The next step is a bounded execution gate, not unrestricted execution.
