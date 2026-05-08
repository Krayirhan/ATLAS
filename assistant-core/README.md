# assistant-core

`assistant-core` is the Python CLI and local assistant runtime foundation for ATLAS.

## Current Scope

The package now contains:

- Preview-only action, permission, device, home, routine, reminder, calendar, panel, and demo flows
- Mock voice pipeline with no real microphone runtime
- Read-only agent layer
- Sprint 51 hardening layer under `app/quality`
- Sprint 52 Safe Execution Gate planning layer under `app/execution`

It still does not contain real PC execution, real home execution, a scheduler, OS notification delivery, external calendar writes, microphone capture, wake word, or a shell executor.

## Sprint 52 Additions

| Area | Sprint 52 status |
|---|---|
| `app/execution` | Added execution models, allowlist, policy, gate, service, and audit helpers |
| `ai execution` | Added CLI for `--preview`, `--from-panel`, `--check-allowlist`, `--json`, `--show-audit`, `--mode`, and `--execute` |
| Allowlist | Added low-risk planning entries for `chrome`, `notepad`, `calculator`, `vscode` |
| Panel handoff | Added approved panel item to execution candidate mapping |
| Runtime safety | `execution_enabled=false` by default; `execute()` stays disabled |
| Tests | Added execution models, allowlist, gate, and CLI regressions |

## Main Packages

| Package | Role |
|---|---|
| `app/actions` | Intent/action/risk/permission contracts and deterministic routing |
| `app/conversation` | Text-first conversation loop and response shaping |
| `app/control` | PC preview planning only |
| `app/execution` | Safe execution planning, allowlist checks, panel handoff, disabled executor |
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
python -m app.cli ai hardening --project ATLAS --all --json
python -m app.cli ai execution --project ATLAS --preview "Chrome'u ac"
python -m app.cli ai execution --project ATLAS --check-allowlist pc.open_app
python -m app.cli ai execution --project ATLAS --show-audit --preview "Chrome'u ac"
```

## Execution Boundary

Everything in `assistant-core` remains preview-first or planning-only:

- `execution_attempted=false` stays the default contract across preview and execution-planning flows
- Panel approval does not start execution
- `ExecutionGate.execute()` does not call `subprocess`, `os.startfile`, PowerShell, cmd, or shell
- Allowlist matches canonical app names only; user text is not converted into command strings or executable paths
- Home/device flows do not touch physical devices or use the network
- Reminder/calendar flows do not start schedulers or external writes
- Voice flow does not use a real microphone and does not retain audio
- Demo, hardening, and execution-planning flows do not open shell execution paths

## Artifact Policy

- Demo artifacts: `workspace/outputs/demo/`
- Hardening artifacts: `workspace/outputs/hardening/`
- Generated reports: `workspace/outputs/reports/`
- Local state: `workspace/state/*.json`

New generated artifacts are local outputs, not source deliverables.
