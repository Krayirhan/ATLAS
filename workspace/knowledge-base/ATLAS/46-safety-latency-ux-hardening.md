# Sprint 51 - Safety / Latency / UX Hardening

## Sprint 51 Purpose

Sprint 51 hardens the Sprint 50 preview demo into a clearer and safer V1 demo baseline without opening real execution.

## Safety Invariant List

The following must remain `false` across demo and preview surfaces:

- `execution_attempted`
- `real_execution_attempted`
- `physical_device_touched`
- `network_used`
- `microphone_used`
- `wake_word_used`
- `audio_retained`
- `external_calendar_used`
- `os_notification_sent`
- `credential_accessed`
- `shell_used`
- `unrestricted_shell_available`
- `execution_gate_enabled`

The following must remain `true` across the same surfaces:

- `allowlist_required`
- `panel_approval_required`

Covered surfaces:

- demo scenarios
- chat / PC preview
- voice pipeline
- home preview
- panel submit / approve
- reminder
- calendar
- routine
- device flow
- notification preview

## Latency Budget

Targets:

- deterministic local CLI surface: under `1500 ms`
- mock voice surface: under `2500 ms`
- heavier `ai demo --all --no-write`: under `7000 ms`

## Hardening CLI Usage

```powershell
python -m app.cli ai hardening --project ATLAS --safety
python -m app.cli ai hardening --project ATLAS --latency
python -m app.cli ai hardening --project ATLAS --all --json
python -m app.cli ai hardening --project ATLAS --all --markdown --no-write
```

Rules:

- no real execution
- no path traversal outside `workspace/outputs/hardening/`
- deterministic preview modules only

## Confirmation Timeout / Cancel Policy

Panel items use an explicit timeout model:

- `default_timeout_seconds`
- `expires_at`

Approval rules:

- expired item cannot be approved
- cancelled item cannot be approved
- denied item cannot be approved
- blocked item cannot be approved
- clarification-required item cannot be approved
- approve records state only

## Voice Confirmation Safety

- medium/high voice requests require explicit confirmation wording
- high-risk voice requests do not accept a short `evet` as sufficient
- low-confidence transcript goes to clarification
- response may explicitly say `Sesli komut olarak algilandi`
- real microphone remains disabled

## CLI Turkish UX Rules

The user-facing CLI should prefer wording that makes preview status obvious:

- `onizleme`
- `gercek islem yapilmadi`
- `onay gerekiyor`
- `engellendi`
- `belirsiz hedef`
- `hatirlatici taslagi`
- `takvim taslagi`
- `mock ses akisi`
- `gercek mikrofon kullanilmadi`

## Generated Artifact Policy

- `workspace/outputs/demo/` for demo artifacts
- `workspace/outputs/hardening/` for hardening artifacts
- `workspace/outputs/reports/` for generated reports
- `workspace/state/*.json` for local runtime state

These are local artifacts. New generated outputs should not be committed as source deliverables.

## What Remains Non-Executable

- real PC execution
- real home execution
- real scheduler
- real OS notification
- real external calendar API
- real microphone capture
- wake word / always-listening
- shell / terminal executor

## Sprint 52 Carry-Forward

Sprint 52 consumes this hardening baseline and preserves it:

- `execution_attempted=false` stays false for preview and disabled execution-planning paths
- `real_execution_attempted=false` stays false for all `ai execution` flows
- shell, PowerShell, and cmd remain blocked
- panel approval does not start execution
- voice, home, scheduler, notification, and calendar boundaries stay closed

Sprint 53 may open only a very small low-risk PC runtime if these hardening invariants stay green.
