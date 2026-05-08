# ATLAS - Current Status

## Release Baseline

- **Release:** V1 RC - GO for preview-first assistant flows.
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
- **Sprint 52:** Safe Execution Gate / Low-Risk PC Execution Planning completed

## Sprint 52 Outcome

Sprint 52 adds the first bounded execution-planning layer without opening real execution.

Completed in Sprint 52:

- `app/execution` package
- `ExecutionPlan`, `ExecutionDecision`, `ExecutionPreparationResult`, `ExecutionResult`
- low-risk allowlist model for `chrome`, `notepad`, `calculator`, `vscode`
- `ExecutionGate.evaluate()` and `ExecutionGate.prepare_*()` flow
- panel approved item to execution candidate handoff
- `ai execution` CLI
- default-off execution policy with `execution_enabled=false`
- blocked policy for PowerShell, cmd, unrestricted shell, destructive file ops, secret reads, and registry edits

## Available User-Facing Preview / Planning Surfaces

- `ai chat`
- `ai voice`
- `ai pc-preview`
- `ai execution`
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

Preview and execution-planning flows must keep these invariants false:

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
- `app/execution`: Safe Execution Gate, allowlist, disabled executor
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
python -m app.cli ai execution --project ATLAS --allowlist
python -m app.cli ai execution --project ATLAS --prepare "Chrome'u ac"
python -m app.cli ai demo --project ATLAS --all --show-safety
python -m app.cli ai hardening --project ATLAS --all --json
python -m app.cli ai docs-audit --project ATLAS --provider mock --scope all-light
python -m app.cli ai security-audit --project ATLAS --provider mock --scope all-light
python -m app.cli audit v1-rc
```

## Next Sprint

Sprint 53 is **Low-Risk PC Execution MVP**.

The next step is still a very small bounded runtime, not unrestricted execution.
