# ATLAS Action Architecture

## Purpose

The action architecture defines how ATLAS turns user intent into safe, previewable, auditable actions.

## Action Lifecycle

```text
intent -> action candidate -> validation -> risk classification -> preview -> confirmation/block -> adapter execution -> result/audit
```

No action should execute directly from natural language.

## Action Schema

Canonical fields:

| Field | Purpose |
|---|---|
| `action_id` | Unique action instance id |
| `action_type` | Namespaced action type |
| `target` | App, folder, file, device, routine, browser query, etc. |
| `parameters` | Structured parameters |
| `risk_level` | `low`, `medium`, `high`, or `blocked` |
| `requires_confirmation` | Whether explicit user confirmation is required |
| `dry_run_supported` | Whether preview can validate without execution |
| `reversible` | Whether action can be undone |
| `source` | CLI, text, voice, desktop, mobile |
| `user_goal` | Original user goal |
| `expected_result` | What should happen if action succeeds |
| `audit_metadata` | Decision, timestamp, routing, confidence, policy metadata |

## Action Types

Initial action type examples:

| Action type | Description | Default risk |
|---|---|---|
| `pc.open_app` | Open a known local application | low |
| `pc.open_folder` | Open a folder path | low/medium |
| `pc.media.play_pause` | Toggle media playback | low |
| `pc.system_info` | Read system information | low |
| `browser.search` | Open/search a query in browser | low/medium |
| `routine.run` | Run a named routine | medium by default |
| `reminder.create` | Create local reminder | low/medium |
| `device.turn_on` | Turn on a device | medium/high |
| `device.turn_off` | Turn off a device | medium/high |
| `device.set_brightness` | Set brightness for a device | medium |

## Risk Levels

| Risk level | Meaning | Handling |
|---|---|---|
| `low` | Read-only, reversible, or low-impact action | preview optional; auto only in later phases |
| `medium` | Changes local state or visible environment | explicit confirmation |
| `high` | Could disrupt work, privacy, home devices, or irreversible state | explicit confirmation plus warning |
| `blocked` | Forbidden or too risky | no execution |

## Intent to Action Rules

- Unknown intent does not produce executable action.
- Ambiguous target asks clarification.
- Voice-originated action uses stricter confirmation.
- Home/device action requires device id, room, capability, and current state when available.
- Routine action previews all child actions before execution.

## Dry-Run and Preview

Dry-run should answer:

- What action would run?
- What target would be affected?
- What parameters would be used?
- What risk level applies?
- Is confirmation required?
- Is the action reversible?
- What could go wrong?

## Result Model

Every action returns:

- `status`: `success`, `cancelled`, `blocked`, `failed`, `needs_confirmation`, `needs_clarification`
- `summary`
- `details`
- `audit_id`
- `warnings`
- `next_step`

## Initial Blocked Categories

- file delete
- recursive delete
- shutdown/restart
- app install
- registry edit
- admin command
- git destructive command
- full disk read/write
- secret file read
- home/device write without registry and permission

## Sprint 37 Focus

Sprint 37 should define the schema and examples only. It should not implement PC control, voice runtime, home control, or new CLI execution commands.
