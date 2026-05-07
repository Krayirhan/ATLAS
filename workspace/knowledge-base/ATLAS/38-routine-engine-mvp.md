# Sprint 43 - RoutineEngine MVP

## Purpose

Sprint 43 adds a preview-only routine layer to ATLAS so repeated personal workflows can be modeled safely before any real execution exists.

## RoutineEngine Role

`RoutineEngine` is the routine planning layer under `app/routines`.

Responsibilities:

- define routine models
- expose built-in routine templates
- preview routine steps
- aggregate routine risk
- evaluate each step through `PermissionManager`
- return dry-run routine results

Non-responsibilities:

- no PC execution
- no home/device execution
- no shell or PowerShell execution
- no scheduler or daemon
- no background automation

## Built-In Routines

- `calisma modu`
- `oyun modu`
- `uyku modu`
- `toplanti modu`
- `eve geldim`
- `evden cikiyorum`

## Routine Models

Core models:

- `RoutineDefinition`
- `RoutineStep`
- `RoutinePreview`
- `RoutineResult`
- `RoutineStepResult`
- `RoutineCategory`
- `RoutineSource`
- `RoutineStatus`

## Preview Flow

```text
User text
  -> RoutineService.parse_routine_request
  -> RoutineEngine.preview_routine / run_routine
  -> RoutineStep -> ActionCandidate
  -> PermissionManager.build_preview / decide
  -> RoutinePreview or RoutineResult
```

## Risk Rules

- any blocked step blocks the routine
- any high-risk step makes the routine high risk
- any medium-risk step requires confirmation
- home/device steps are at least medium risk
- `pc.lock` and similar high-impact steps escalate the routine
- execution remains dry-run only

## PermissionManager Integration

Every routine step is converted into an `ActionCandidate` and evaluated by `PermissionManager`.

Outputs included in `RoutinePreview`:

- per-step permission decisions
- aggregated routine risk
- routine confirmation requirement
- blocked reason if any
- audit metadata with `execution_attempted=false`

## PersonalMemory Integration

Sprint 43 includes optional read-only preference lookup:

- generic app targets can be replaced by remembered preferences
- routines do not write memory
- stale preferences remain a known risk and must be handled conservatively

## ConversationLoop Integration

`ai chat` can now answer routine requests safely:

- `Calisma modunu baslat`
- `Oyun modunu ac`
- `Uyku modunu baslat`
- `Rutinleri goster`
- `Evden cikiyorum`

These flows remain preview-only and do not execute adapters.

## CLI Examples

```powershell
python -m app.cli ai routine --project ATLAS --list
python -m app.cli ai routine --project ATLAS "Calisma modunu baslat"
python -m app.cli ai routine --project ATLAS --show-preview "Uyku modunu baslat"
python -m app.cli ai routine --project ATLAS --json "Evden cikiyorum"
```

## Execution Boundary

- `run_routine()` always returns `executed=false`
- `run_routine()` always returns `dry_run=true`
- no scheduler exists
- no adapter execute call exists
- no home/device runtime exists
- no terminal executor exists

## Test Plan

Validation targets:

- routine templates exist
- routine preview returns aggregated risk
- medium/high routines require confirmation
- blocked routines remain blocked
- CLI outputs preview/result safely
- conversation loop routine path works
- personal memory flow stays intact

## Acceptance Criteria

- built-in routine preview exists
- step-level permission decisions exist
- routine confirmation/blocked behavior is aggregated correctly
- routine CLI works
- conversation loop routine support works
- no execution boundary is crossed

## Next Dependency

Sprint 44 should define **Voice Core Architecture** before any microphone runtime is added.
