# ATLAS AI Assistant

## Product Vision

ATLAS is a local-first personal AI assistant foundation for Windows. It is built around explicit permission handling, preview-first action planning, bounded local state, and strict non-shell safety boundaries.

ATLAS is still not a real execution assistant. Sprint 52 adds the Safe Execution Gate planning layer, but real PC and home execution remain disabled.

## Current Status

| Item | Value |
|---|---|
| Release baseline | V1 RC - GO for preview-first assistant flows |
| Current sprint | Sprint 52 - Safe Execution Gate / Low-Risk PC Execution Planning completed |
| Root | `E:\ATLAS` |
| Assistant core | `E:\ATLAS\assistant-core` |
| Knowledge base | `E:\ATLAS\workspace\knowledge-base\ATLAS` |
| Default provider | `ollama` |
| Validation | `python -m pytest -q`, `python -m app.cli doctor --full` |

Sprint 51 hardened the V1 demo. Sprint 52 adds a bounded execution-planning layer under `app/execution`, a low-risk allowlist, panel-to-execution handoff modeling, typed execution plan/result contracts, and a new `ai execution` CLI. This sprint still does not open real app launch, shell, PowerShell, cmd, or process execution.

## What Works Now

- Text-first conversation preview through `ai chat`
- Mock voice preview through `ai voice`
- PC preview planning through `ai pc-preview`
- Safe Execution Gate planning through `ai execution`
- Device and home preview flows through `ai device` and `ai home-preview`
- Reminder draft, calendar draft/query preview, and notification preview flows
- Permission panel backend through `ai panel`
- End-to-end demo runner through `ai demo`
- Hardening audit surface through `ai hardening`
- Read-only agent layer: `MainAgent`, `ToolApprovalAgent`, `SecurityAuditorAgent`, `DocumentationAgent`, `PlannerAgent`, `ProjectQAAgent`, `MemoryAgent`

## Sprint 52 Highlights

- Added `app/execution` package:
  `models.py`, `allowlist.py`, `policy.py`, `gate.py`, `service.py`, `audit.py`
- Added typed models:
  `ExecutionPlan`, `ExecutionDecision`, `ExecutionPreparationResult`, `ExecutionResult`
- Added low-risk allowlist items:
  `chrome`, `notepad`, `calculator`, `vscode`
- Added policy rules:
  `PowerShell`, `cmd`, unrestricted shell, secret/credential reads, destructive file ops, and registry edits stay blocked
- Added panel-to-execution handoff:
  approved panel items can be mapped into execution candidates, but `execution_enabled=false` keeps runtime disabled
- Added CLI:
  `python -m app.cli ai execution --project ATLAS --allowlist`
  `python -m app.cli ai execution --project ATLAS --prepare "Chrome'u ac"`
  `python -m app.cli ai execution --project ATLAS --show-policy`

## Key Commands

```powershell
cd E:\ATLAS\assistant-core

python -m pytest -q
python -m app.cli doctor --full
python -m app.cli config validate
python -m app.cli project validate ATLAS

python -m app.cli ai demo --project ATLAS --all --show-safety
python -m app.cli ai hardening --project ATLAS --all --json
python -m app.cli ai execution --project ATLAS --allowlist
python -m app.cli ai execution --project ATLAS --prepare "Chrome'u ac"
python -m app.cli ai execution --project ATLAS --show-policy
```

## Execution Boundary

Sprint 52 still forbids:

- No real Chrome, Notepad, Calculator, or VS Code launch
- No real folder opening
- No `subprocess.run`, `os.startfile`, PowerShell, cmd, or shell executor
- No file delete, move, overwrite, or registry edit execution
- No real Home Assistant, MQTT, or physical device control
- No real scheduler, OS notification delivery, or external calendar write
- No real microphone capture
- No wake word / always-listening
- No credential or `.env` reading

`ExecutionGate.execute()` always returns a safe non-executing result in Sprint 52.

## Artifact Policy

- Demo reports belong under `workspace/outputs/demo/`
- Hardening reports belong under `workspace/outputs/hardening/`
- Generated V1/report artifacts stay under `workspace/outputs/reports/`
- Local runtime state stays under `workspace/state/*.json`
- Generated artifacts are local outputs and should not be newly committed

## Next Sprint

Sprint 53 is **Low-Risk PC Execution MVP**.

The next step is still not broad execution. Sprint 53 should open, at most, a very small low-risk app-open runtime under the Safe Execution Gate with explicit audit and rollback constraints.

## Repo

https://github.com/Krayirhan/ATLAS
