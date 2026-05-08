# Sprint 48 / 51 / 52 - Desktop Permission Panel Backend

## Purpose

The permission panel remains a backend and CLI visibility layer. Sprint 51 hardened its approval policy. Sprint 52 adds a planning-only handoff into the Safe Execution Gate without opening execution.

## Current Capabilities

- submit / list / show / approve / deny / cancel / clear
- safe local JSON or in-memory store
- blocked / clarification / confirmation visibility
- reminder and calendar item support
- approved panel item to execution candidate handoff
- approve remains preview-only

## Confirmation Timeout / Cancel Policy

Each actionable item carries:

- `default_timeout_seconds`
- `expires_at`

Rules:

- expired pending item cannot be approved
- cancelled item cannot be approved
- denied item cannot be approved
- blocked item cannot be approved
- clarification-required item cannot be approved
- approved item cannot be replay-approved

Timeout outcome:

- stale items move to `expired`
- user-driven abort moves to `cancelled`

## Approval Boundary

Approve means:

- user confirmation was recorded
- item moves to `approved_preview`
- `execution_attempted=false`
- `execution_allowed=false`
- no scheduler starts
- no calendar write starts
- no PC/home execution starts

## Sprint 52 Handoff Boundary

Sprint 52 now adds a planning-only handoff:

- approved panel item may be mapped into an execution candidate
- the handoff goes through `SafeExecutionGate`, not directly to a runtime
- `execution_enabled=false` keeps runtime execution disabled
- expired / denied / cancelled / blocked / clarification-required items still cannot pass
- panel approve remains a state change only
- approved item result is `armed_for_future`, not `executed`

## Copy Rule

Every panel surface must make this clear:

`Bu sadece onizlemedir; gercek islem yapilmadi.`

For approved items:

`Onay kaydedildi ama gercek islem baslatilmadi.`

## Current Non-Goals

- no real tray runtime
- no GUI framework
- no notification badge runtime
- no background daemon
- no real execution handoff

## Sprint 53 Dependency

If ATLAS ever introduces a real low-risk PC runtime, panel handoff must remain explicit, separately audited, and bounded by the Safe Execution Gate.
