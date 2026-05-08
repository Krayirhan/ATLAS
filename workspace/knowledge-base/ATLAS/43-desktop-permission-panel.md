# Sprint 48 / 51 - Desktop Permission Panel Backend

## Purpose

The permission panel remains a backend and CLI visibility layer. Sprint 51 hardens its approval policy without opening execution.

## Current Capabilities

- submit/list/show/approve/deny/cancel/clear
- safe local JSON or in-memory store
- blocked / clarification / confirmation visibility
- reminder and calendar item support
- approve remains preview-only

## Confirmation Timeout / Cancel Policy

Each actionable item now carries:

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

## Copy Rule

Every panel surface must make this clear:

`Bu sadece onizlemedir; gercek islem yapilmadi.`

## Current Non-Goals

- no real tray runtime
- no GUI framework
- no notification badge runtime
- no background daemon
- no execution handoff yet

## Sprint 52 Dependency

If ATLAS ever introduces a safe execution gate, panel handoff must remain explicit and separately audited.
