# Sprint 38 - PermissionManager Flow

## Purpose

Sprint 38 builds the non-executing permission decision layer for ATLAS personal actions. It consumes Sprint 37 `ActionCandidate` contracts and produces preview, confirmation, clarification, block, deny, cancel, result, and audit metadata models.

This sprint does not execute real actions.

## PermissionManager Role

`PermissionManager` is the personal action approval layer under `app/actions`.

Responsibilities:

- Accept `ActionCandidate`.
- Build `ActionPreview`.
- Produce `PermissionDecision`.
- Map risk to permission status.
- Require confirmation for medium/high actions.
- Block forbidden actions.
- Send ambiguous/unknown/missing-target actions to clarification.
- Apply stricter voice-source rules.
- Produce audit metadata.
- Return model-only `ActionResult` for confirm, deny, and cancel.

Non-responsibilities:

- No PC control.
- No home control.
- No voice runtime.
- No adapter calls.
- No terminal or PowerShell execution.
- No file operation execution.

## ToolApprovalAgent Difference

| System | Scope | Runtime position |
|---|---|---|
| `ToolApprovalAgent` | Devtools command/file/tool/git/MCP preview | Parked/supporting devtools subsystem |
| `PermissionManager` | Personal assistant action approval | Core personal action safety layer |

Both are security-first and preview-only today, but they evaluate different objects. `ToolApprovalAgent` evaluates proposed commands/tools. `PermissionManager` evaluates canonical personal action candidates.

## Canonical Flow

```text
ActionCandidate
  -> Risk classification
  -> ActionPreview
  -> PermissionDecision
  -> confirm / deny / block / cancel / clarification
  -> ActionResult
  -> audit metadata
```

## PermissionDecision Fields

| Field | Meaning |
|---|---|
| `action_id` | Candidate action id |
| `status` | Permission status |
| `risk_level` | Risk used by decision |
| `allowed_to_execute` | Future adapter permission indicator |
| `requires_confirmation` | Explicit confirmation needed |
| `requires_clarification` | Clarification needed before action |
| `blocked` | Action forbidden |
| `reason` | Decision reason |
| `confirmation_prompt` | Prompt copy |
| `warnings` | Risk warnings |
| `audit_metadata` | Audit-ready metadata |
| `next_step` | Caller guidance |

## Status List

- `safe_readonly`
- `preview_allowed`
- `confirmation_required`
- `clarification_required`
- `denied`
- `blocked`
- `cancelled`
- `unknown`

## Risk Level Mapping

| Risk | Decision | Confirmation | Notes |
|---|---|---|---|
| `safe_readonly` | `safe_readonly` | No | Read-only result path only |
| `low` | `preview_allowed` | Usually no | Future adapter only after explicit implementation |
| `medium` | `confirmation_required` | Yes | State-changing action |
| `high` | `confirmation_required` | Yes + warning | Work, privacy, or physical impact |
| `blocked` | `blocked` | No | Never reaches adapter |

## Clarification Rules

Return `clarification_required` when:

- intent is `ambiguous`
- intent is `unknown`
- target is missing
- voice confidence is below threshold
- source/target/parameters are not sufficient for a safe preview

Safe default is no action.

## Voice-Source Rules

For `source=voice`:

- low confidence returns `clarification_required`
- medium/high returns `confirmation_required`
- prompt repeats that the command was heard as voice
- target must be explicit
- blocked remains blocked

## Blocked Action Rules

Blocked actions:

- do not ask for confirmation as if execution were possible
- set `blocked=true`
- set `allowed_to_execute=false`
- include blocked reason
- include audit metadata
- suggest a safe alternative

Examples:

- `file.delete`
- `file.overwrite`
- `secret.read`
- `credential.read`
- `registry.edit`
- `shell.execute_unrestricted`
- `full_disk_scan`

## Audit Metadata

Sprint 38 audit metadata includes:

- `action_id`
- `action_type`
- `intent_category`
- `risk_level`
- `source`
- `decision_status`
- `requires_confirmation`
- `blocked`
- `target_summary`
- `created_at`
- `policy_version`
- `execution_attempted=false`

`execution_attempted` must remain false for every Sprint 38 path.

## Confirmation Examples

Medium:

```text
salon isigi hedefinde device.turn_on yapmami onayliyor musun?
```

High:

```text
Yuksek riskli islem: bilgisayar hedefinde pc.shutdown yapmak uzeresin. Acik calismalar, gizlilik veya fiziksel ortam etkilenebilir. Devam etmemi acikca onayliyor musun?
```

Voice:

```text
Sesli komut olarak algiladim. Sunu yapmak istedigini onayliyor musun: salon isigi hedefinde device.turn_on yapmami onayliyor musun?
```

Blocked:

```text
Bu islem guvenlik politikasi nedeniyle calistirilamaz: file.delete MVP'de engellidir.
```

Ambiguous:

```text
Komutu netlestirmem gerekiyor. Hedef, oda, cihaz veya islem adini belirt.
```

## Execution Boundary

Sprint 38 has no execution boundary crossing:

- `PermissionManager` never calls an adapter.
- `confirm()` returns an approved `ActionResult` with `executed=false`.
- `deny()` returns denied with `executed=false`.
- `cancel()` returns cancelled with `executed=false`.
- blocked action returns blocked decision/result path.
- no terminal, PC, home, voice, file, or MCP execution exists here.

## Acceptance Criteria

- `safe_readonly`, `low`, `medium`, `high`, and `blocked` mapping works.
- ambiguous/unknown/missing-target clarification works.
- voice-source stricter confirmation works.
- audit metadata includes `execution_attempted=false`.
- ToolApprovalAgent distinction is documented.
- tests cover model-only permission behavior.

## Sprint 39 Outcome

Sprint 39 now feeds text-derived `IntentResult` and `ActionCandidate` objects into PermissionManager through deterministic `IntentRouter` preview routing.

## Next Step

Sprint 40 should implement **PC Control Adapter MVP** and consume approved low/safe preview outputs without bypassing PermissionManager.
