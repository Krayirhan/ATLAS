# ATLAS AI Assistant

## Product Vision

ATLAS is a local-first personal AI assistant foundation for Windows. It is built around safe text and future voice interaction, explicit permission handling, preview-first action planning, and bounded local state.

ATLAS is not a real execution assistant yet. The current product line is a demonstrable V1 preview/control plane.

## Current Status

| Item | Value |
|---|---|
| Release baseline | V1 RC - GO for preview-only assistant flows |
| Current sprint | Sprint 51 - Safety / Latency / UX Hardening completed |
| Root | `E:\ATLAS` |
| Assistant core | `E:\ATLAS\assistant-core` |
| Knowledge base | `E:\ATLAS\workspace\knowledge-base\ATLAS` |
| Default provider | `ollama` |
| Validation | `python -m pytest -q`, `python -m app.cli doctor --full` |

Sprint 50 brought the end-to-end personal assistant demo together. Sprint 51 hardens that demo with a central safety invariant suite, latency reporting, a new `ai hardening` CLI, stricter panel timeout/cancel behavior, stronger voice confirmation copy, and clearer Turkish preview UX.

## What Works Now

- Text-first conversation preview through `ai chat`
- Mock voice preview through `ai voice`
- PC preview planning through `ai pc-preview`
- Device and home preview flows through `ai device` and `ai home-preview`
- Reminder draft, calendar draft/query preview, and notification preview flows
- Permission panel backend through `ai panel`
- End-to-end demo runner through `ai demo`
- Hardening audit surface through `ai hardening`
- Read-only agent layer: `MainAgent`, `ToolApprovalAgent`, `SecurityAuditorAgent`, `DocumentationAgent`, `PlannerAgent`, `ProjectQAAgent`, `MemoryAgent`

## Sprint 51 Highlights

- Safety invariants are validated centrally:
  `execution_attempted`, `physical_device_touched`, `network_used`, `microphone_used`, `wake_word_used`, `audio_retained`, `external_calendar_used`, `os_notification_sent`, `credential_accessed`, `shell_used`
- `python -m app.cli ai hardening --project ATLAS` supports:
  `--safety`, `--latency`, `--all`, `--json`, `--markdown`, `--no-write`, `--output`
- Latency budgets exist for:
  `ai chat`, `ai voice`, `ai routine`, `ai reminder`, `ai calendar`, `ai panel`, `ai home-preview`, `ai demo --all`
- Permission panel runtime now has explicit confirmation timeout policy and blocks approve on expired/cancelled/denied/blocked/clarification items.
- Voice runtime stays mock-only, keeps `execution_attempted=false`, and uses stricter confirmation wording for risky voice requests.
- CLI copy now emphasizes `onizleme`, `onay gerekiyor`, `engellendi`, `belirsiz hedef`, `hatirlatici taslagi`, `takvim taslagi`, `mock ses akisi`, and `gercek islem yapilmadi`.

## Key Commands

```powershell
cd E:\ATLAS\assistant-core

python -m pytest -q
python -m app.cli doctor --full
python -m app.cli config validate
python -m app.cli project validate ATLAS

python -m app.cli ai demo --project ATLAS --all --show-safety
python -m app.cli ai hardening --project ATLAS --all --markdown --no-write
python -m app.cli ai chat --project ATLAS "Chrome'u aç"
python -m app.cli ai voice --project ATLAS --mock-transcript "Salon ışığını aç" --show-safety
python -m app.cli ai panel --project ATLAS --submit "Salon ışığını aç"
```

## Execution Boundary

These remain out of scope in Sprint 51:

- No real Chrome/app opening
- No real folder opening
- No real Home Assistant or MQTT runtime
- No physical device state change
- No real OS notification delivery
- No real external calendar API
- No real microphone capture
- No wake word / always-listening
- No background scheduler / daemon
- No shell / terminal executor
- No credential or `.env` reading

## Artifact Policy

- Demo reports belong under `workspace/outputs/demo/`
- Hardening reports belong under `workspace/outputs/hardening/`
- Generated V1/report artifacts stay under `workspace/outputs/reports/`
- Local runtime state stays under `workspace/state/*.json`
- Generated artifacts should not be committed as new Sprint 51 outputs

Historical tracked report artifacts already exist under `workspace/outputs/reports/`; Sprint 51 keeps them as history but treats new generated outputs as local artifacts.

## Next Sprint

Sprint 52 is **Safe Execution Gate / Low-Risk PC Execution Planning**.

The next step is not broad execution. The next step is a tightly bounded execution gate for a small, explicit low-risk PC allowlist, with audit, rollback expectations, and unchanged blocked/high-risk boundaries.

## Repo

https://github.com/Krayirhan/ATLAS
