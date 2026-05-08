# Sprint 52 - Safe Execution Gate Planning

## Purpose

Sprint 52 introduces `SafeExecutionGate` as the first bounded execution-planning layer for ATLAS. The goal is to model low-risk PC execution eligibility without opening real runtime execution.

## SafeExecutionGate Role

- accept `ExecutionRequest`
- evaluate policy + allowlist eligibility
- build an auditable `ExecutionPlan`
- return non-executing `ExecutionResult`
- support `cancel()` and `deny()` contract outputs

Real execution is still disabled.

## Allowlist Model

Allowed action types for planning:

- `pc.open_app`
- `pc.open_folder`
- `pc.system_info`
- `browser.search`
- `pc.media.play_pause`
- `pc.media.next`
- `pc.media.previous`
- `pc.volume.set`
- `pc.volume.mute_toggle`

Canonical app targets:

- `Chrome`
- `Notepad`
- `Calculator`
- `VS Code`

Unknown targets are not eligible.

## Explicitly Blocked Actions

- `shell.execute`
- `shell.execute_unrestricted`
- `powershell.run`
- `cmd.run`
- `file.delete`
- `file.overwrite`
- `file.move`
- `registry.edit`
- `app.install`
- `app.uninstall`
- `credential.read`
- `secret.read`
- `full_disk_scan`
- `admin.operation`
- `device.turn_on`
- `device.turn_off`
- `home.write_state`
- `mqtt.publish`
- `home_assistant.call_service`

## Panel To Execution Handoff

- panel approval does not execute anything
- approved item can become only an `armed_for_future` execution result
- blocked, clarification-required, denied, cancelled, and expired items cannot pass handoff
- panel replay protection depends on status and expiry validation

## Execution Disabled By Default

- `execution_enabled=false`
- default mode is `preview_only`
- `--execute` still does not trigger runtime execution
- no shell, PowerShell, cmd, `subprocess`, or path-based execution exists

## Low-Risk PC Eligibility

An action may be marked eligible only when:

- policy allows it
- allowlist allows it
- target is canonical if required
- risk is not `medium`, `high`, or `blocked`

Even then:

- panel approval is still required
- runtime remains disabled
- result stays `previewed` or `armed_for_future`

## Audit Metadata

Execution audit metadata includes:

- `execution_id`
- `action_type`
- `target`
- `source`
- `risk_level`
- `permission_status`
- `panel_status`
- `allowlist_decision`
- `execution_enabled`
- `requested_mode`
- `real_execution_attempted=false`
- `shell_used=false`
- `network_used=false`
- `physical_device_touched=false`
- `credential_accessed=false`
- `created_at`

## Rollback / Cancel Model

- rollback exists as a contract only
- no runtime rollback implementation exists in Sprint 52
- `cancel()` and `deny()` emit non-executing audit-safe results
- rollback metadata must not imply real system state changed

## No Shell / No Home Execution Policy

- no unrestricted shell
- no PowerShell
- no `cmd.exe`
- no file delete/move/overwrite
- no registry edit
- no admin action
- no device/home physical execution
- no OS notification or scheduler execution

## CLI Usage

```powershell
python -m app.cli ai execution --project ATLAS --preview "Chrome'u ac"
python -m app.cli ai execution --project ATLAS --preview "Sifrelerimi oku"
python -m app.cli ai execution --project ATLAS --preview "Salon isigini ac"
python -m app.cli ai execution --project ATLAS --check-allowlist pc.open_app
python -m app.cli ai execution --project ATLAS --json --preview "Chrome'u ac"
python -m app.cli ai execution --project ATLAS --show-audit --preview "Chrome'u ac"
python -m app.cli ai execution --project ATLAS --execute --preview "Chrome'u ac"
```

## Test Plan

- model construction tests
- allowlist allow/block tests
- gate eligibility and blocked-path tests
- panel handoff tests
- CLI regression tests
- hardening invariant extension for execution-gate flags

## Sprint 53 Dependency

Sprint 53 may open only a very small low-risk PC execution MVP after:

- these gate tests stay green
- no shell path exists
- allowlist spoofing stays blocked
- panel replay and expiry handling stay explicit
- audit coverage stays complete
