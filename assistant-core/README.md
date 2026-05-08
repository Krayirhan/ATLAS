# assistant-core

`assistant-core` is the Python CLI and local assistant runtime foundation for ATLAS.

## Current Scope

The package now contains:

- Preview-only action, permission, device, home, routine, reminder, calendar, panel, and demo flows
- Mock voice pipeline with no real microphone runtime
- Read-only agent layer
- Sprint 51 hardening layer under `app/quality`

It still does not contain real PC execution, real home execution, a scheduler, OS notification delivery, external calendar writes, microphone capture, wake word, or a shell executor.

## Sprint 51 Additions

| Area | Sprint 51 status |
|---|---|
| `app/quality` | Added safety suite, latency suite, hardening report models, report formatter |
| `ai hardening` | Added CLI for `--safety`, `--latency`, `--all`, `--json`, `--markdown`, `--no-write`, `--output` |
| `app/panel` | Added explicit confirmation timeout policy; approve rules tightened |
| `app/voice` | Added stricter runtime confirmation copy and low-confidence clarification behavior |
| CLI UX | Preview vs execution wording clarified in Turkish |
| Tests | Added safety, latency, hardening CLI, and approval timeout regressions |

## Main Packages

| Package | Role |
|---|---|
| `app/actions` | Intent/action/risk/permission contracts and deterministic routing |
| `app/conversation` | Text-first conversation loop and response shaping |
| `app/control` | PC preview planning only |
| `app/devices` | Device registry, alias resolution, capability-aware preview planning |
| `app/home` | Mock home preview adapter, no network/device execution |
| `app/panel` | Pending approval queue and preview-only state changes |
| `app/personal_assistant` | Reminder draft, calendar draft/query, notification preview |
| `app/voice` | Mock STT/TTS pipeline, no real microphone |
| `app/demo` | End-to-end preview demo runner and report generation |
| `app/quality` | Sprint 51 safety and latency hardening suite |

## Important Commands

```powershell
cd E:\ATLAS\assistant-core

python -m pytest -q
python -m app.cli doctor --full
python -m app.cli ai demo --project ATLAS --all --show-safety
python -m app.cli ai hardening --project ATLAS --all --markdown --no-write
```

## Execution Boundary

Everything in `assistant-core` remains preview-first:

- `execution_attempted=false` is the default contract across preview flows
- Panel approval does not start execution
- Home/device flows do not touch physical devices or use the network
- Reminder/calendar flows do not start schedulers or external writes
- Voice flow does not use a real microphone and does not retain audio
- Demo and hardening flows do not open shell execution paths

## Artifact Policy

- Demo artifacts: `workspace/outputs/demo/`
- Hardening artifacts: `workspace/outputs/hardening/`
- Generated reports: `workspace/outputs/reports/`
- Local state: `workspace/state/*.json`

New generated artifacts are local outputs, not Sprint 51 source deliverables.
