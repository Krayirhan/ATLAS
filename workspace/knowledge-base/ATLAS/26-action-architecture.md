# ATLAS Action Architecture

## Purpose

The action architecture defines how ATLAS turns user intent into safe, previewable, auditable actions. Sprint 37 makes the Intent and Action contracts canonical. It does not implement real PC, home, voice, terminal, file, or adapter execution.

## Lifecycle

```text
User Input
  -> IntentResult
  -> ActionCandidate
  -> RiskClassifier
  -> ActionPreview
  -> Confirmation / Block
  -> Adapter Execution
  -> ActionResult
  -> Audit
```

No action should execute directly from natural language.

## Intent Schema

Intent answers: "What type of request is the user making?"

| Field | Type | Purpose |
|---|---|---|
| `intent_id` | string | Unique intent instance id |
| `category` | enum | Canonical intent category |
| `confidence` | float | 0.0-1.0 classifier confidence |
| `language` | string | Expected first value: `tr`; text fallback may use `en` |
| `raw_text` | string | Original user input |
| `normalized_text` | string | Normalized command text |
| `entities` | object | Extracted app, folder, room, device, time, value, etc. |
| `target` | string | Primary target if known |
| `action_candidate` | enum/null | Candidate action type if unambiguous |
| `ambiguity_reason` | string | Why clarification is required |
| `requires_clarification` | boolean | True when target/action is unclear |
| `safety_notes` | list | Safety, privacy, or policy notes |

### Intent Categories

| Category | Meaning |
|---|---|
| `conversation.question` | General answer-only question |
| `conversation.status` | Assistant or system status question |
| `personal.memory_query` | Ask remembered preference or personal note |
| `personal.preference_set` | Store/update a preference |
| `pc.open_app` | Open known local application |
| `pc.open_folder` | Open known folder |
| `pc.system_info` | Read system information |
| `pc.media_control` | Play/pause/next/previous media |
| `pc.volume_control` | Set or toggle system volume |
| `browser.search` | Search/open browser query |
| `file.search` | Search files with preview |
| `routine.create` | Define a routine |
| `routine.run` | Run a routine |
| `routine.preview` | Preview routine steps |
| `reminder.create` | Create reminder |
| `calendar.query` | Read calendar information |
| `calendar.event_draft` | Create local calendar draft preview |
| `device.state_query` | Read device state |
| `device.turn_on` | Turn on device |
| `device.turn_off` | Turn off device |
| `device.set_brightness` | Set device brightness |
| `device.set_temperature` | Set thermostat/temperature |
| `unknown` | Cannot classify safely |
| `ambiguous` | Multiple plausible targets/actions |
| `blocked` | Requested action is forbidden |

## Action Schema

Action answers: "What would ATLAS do if the request is approved?"

| Field | Type | Purpose |
|---|---|---|
| `action_id` | string | Unique action instance id |
| `action_type` | enum | Namespaced action type |
| `target` | string | App, folder, file, device, routine, query, etc. |
| `parameters` | object | Structured parameters for future adapter |
| `source` | enum | `text`, `voice`, `routine`, `schedule`, `main_agent`, `manual`, `unknown` |
| `user_goal` | string | Original user goal |
| `intent_category` | enum | Source intent category |
| `risk_level` | enum | `safe_readonly`, `low`, `medium`, `high`, `blocked` |
| `requires_confirmation` | boolean | Whether explicit confirmation is required |
| `dry_run_supported` | boolean | Whether preview can be generated without execution |
| `reversible` | boolean | Whether the result can be undone |
| `expected_result` | string | Human-readable expected outcome |
| `blocked_reason` | string | Required when action is blocked |
| `confirmation_prompt` | string | Prompt shown before approval |
| `audit_metadata` | object | Routing, policy, confidence, and timestamp metadata |

## Action Sources

| Source | Meaning | Risk implication |
|---|---|---|
| `text` | User typed command | Baseline risk |
| `voice` | Voice/STT command | Medium/high requires repeated confirmation |
| `routine` | Routine child action | Risk aggregates into routine risk |
| `schedule` | Scheduled trigger | Requires prior explicit setup and audit |
| `main_agent` | Planned by MainAgent | Must still go through permission |
| `manual` | User-selected UI action | Still risk-classified |
| `unknown` | Missing source | Conservative handling |

## Action Type Inventory

### Safe Read-Only

| Action type | Description | Confirmation |
|---|---|---|
| `pc.system_info` | Read local system status | No |
| `file.search` | Search files and show preview | No |
| `device.state_query` | Read device state | No |
| `calendar.query` | Read calendar information | No |
| `routine.preview` | Preview routine steps | No |
| `reminder.preview` | Preview reminder details | No |

### Low-Risk Safe Actions

| Action type | Description | Confirmation |
|---|---|---|
| `pc.open_app` | Open known application | Usually no; preview/log |
| `pc.open_folder` | Open known folder | Usually no; preview/log |
| `browser.search` | Search/open browser query | Usually no; privacy-sensitive query may escalate |
| `pc.media.play_pause` | Toggle media playback | No |
| `pc.media.next` | Next media item | No |
| `pc.media.previous` | Previous media item | No |
| `pc.volume.set` | Set volume to a numeric value | Usually no; high volume may warn |
| `pc.volume.mute_toggle` | Toggle mute | No |

### Medium-Risk Actions

| Action type | Description | Confirmation |
|---|---|---|
| `reminder.create` | Create reminder | Yes |
| `calendar.event_draft` | Create local calendar draft | Yes |
| `routine.create` | Create routine definition | Yes |
| `routine.run` | Run routine with non-destructive steps | Yes |
| `device.turn_on` | Turn on device | Yes |
| `device.turn_off` | Turn off device | Yes |
| `device.set_brightness` | Set brightness | Yes |
| `device.set_temperature` | Set temperature | Yes |

### High-Risk Actions

| Action type | Description | Confirmation |
|---|---|---|
| `pc.sleep` | Put PC to sleep | Yes + warning |
| `pc.lock` | Lock PC | Yes + warning |
| `pc.shutdown` | Shut down PC | Yes + warning; may remain deferred |
| `device.unlock` | Unlock device | Yes + warning; likely blocked early |
| `device.open_door` | Open door/gate | Yes + warning; likely blocked early |
| `device.disable_security` | Disable security device | Yes + warning; likely blocked early |
| `routine.run_high_impact` | Run high-impact routine | Yes + warning |

### Blocked

| Action type | Reason |
|---|---|
| `file.delete` | Destructive file operation |
| `file.overwrite` | Data loss risk |
| `app.install` | System change and security risk |
| `app.uninstall` | System change and data loss risk |
| `registry.edit` | Windows stability/security risk |
| `shell.execute_unrestricted` | Unbounded terminal execution |
| `credential.read` | Credential access |
| `secret.read` | Secret access |
| `full_disk_scan` | Privacy and scope risk |
| `destructive_system_change` | Broad unsafe system change |

## Risk Model

| Risk level | Meaning | Execution policy |
|---|---|---|
| `safe_readonly` | Reads information only; no state change | Allowed to preview/read in future adapter; audit required |
| `low` | Reversible or low-impact action | Preview/log; auto only after later policy |
| `medium` | Changes local or physical state | Explicit confirmation required |
| `high` | Work disruption, physical, privacy, or irreversible impact | Explicit confirmation + detailed warning required |
| `blocked` | Forbidden or out of MVP policy | No execution; show blocked reason |

### Risk Inputs

Risk classification must consider:

- Reversibility.
- Physical-world effect.
- System state change.
- File/data loss risk.
- Privacy exposure.
- Financial or security effect.
- Voice-source misrecognition risk.
- Low confidence.
- Ambiguous target.
- Required user confirmation.

## Dry-Run and Preview Contract

`ActionPreview` fields:

| Field | Purpose |
|---|---|
| `action_id` | Matches candidate action |
| `summary` | Human-readable summary |
| `target` | Concrete target |
| `parameters_preview` | Sanitized parameter view |
| `risk_level` | Final risk |
| `will_change_state` | Whether state changes |
| `requires_confirmation` | Whether confirmation is required |
| `reversible` | Whether undo is possible |
| `estimated_effect` | What will happen |
| `warnings` | Safety/privacy warnings |
| `safe_to_execute` | True only after policy permits |
| `blocked_reason` | Required when blocked |
| `requires_clarification` | True when no action may proceed before user clarifies |

Rules:

- Medium/high action cannot execute without preview.
- Voice-source medium/high action must repeat understood action and target.
- Ambiguous target does not produce an executable action.
- Ambiguous/unknown action preview uses `requires_clarification=true`.
- Blocked action preview only explains the block.

## ActionResult Contract

`ActionResult` fields:

| Field | Purpose |
|---|---|
| `action_id` | Matches candidate action |
| `status` | Lifecycle status |
| `executed` | Whether adapter actually executed |
| `dry_run` | Whether result is preview-only |
| `message` | User-readable result summary |
| `result_data` | Structured adapter result |
| `error_code` | Stable error code |
| `error_message` | Detailed error text |
| `audit_metadata` | Decision/result metadata |
| `started_at` | Runtime start timestamp |
| `finished_at` | Runtime finish timestamp |

Status values:

- `planned`
- `previewed`
- `awaiting_confirmation`
- `approved`
- `denied`
- `blocked`
- `executed`
- `failed`
- `cancelled`
- `skipped`

## PermissionDecision Contract

Sprint 38 adds `PermissionDecision` as the bridge between preview and any future adapter boundary.

| Field | Purpose |
|---|---|
| `action_id` | Matches candidate action |
| `status` | Permission status |
| `risk_level` | Final risk used by the permission gate |
| `allowed_to_execute` | Whether future adapter execution could be allowed by policy |
| `requires_confirmation` | Whether explicit user confirmation is required |
| `requires_clarification` | Whether the assistant must ask a clarification question |
| `blocked` | Whether execution is forbidden |
| `reason` | Human-readable decision reason |
| `confirmation_prompt` | Prompt text for confirmation or clarification |
| `warnings` | Risk or source warnings |
| `audit_metadata` | Audit-ready metadata with `execution_attempted=false` |
| `next_step` | What the caller should do next |

Status values:

- `safe_readonly`
- `preview_allowed`
- `confirmation_required`
- `clarification_required`
- `denied`
- `blocked`
- `cancelled`
- `unknown`

## PermissionManager Flow

Sprint 38 implements this non-executing decision flow:

```text
ActionCandidate
  -> build_preview()
  -> PermissionDecision
  -> confirm / deny / cancel / block / clarification
  -> ActionResult
```

Rules:

- `safe_readonly` becomes `safe_readonly`, no confirmation.
- `low` becomes `preview_allowed`, no default confirmation.
- `medium` becomes `confirmation_required`.
- `high` becomes `confirmation_required` with warning.
- `blocked` becomes `blocked`.
- `ambiguous` or `unknown` intent becomes `clarification_required`.
- Missing target becomes `clarification_required`.
- Voice-source medium/high requires confirmation.
- Voice-source low confidence becomes `clarification_required`.
- `confirm`, `deny`, and `cancel` return model results only; no adapter is called.
- Audit metadata must always include `execution_attempted=false`.

## Sprint 39 IntentRouter Integration

Sprint 39 adds a deterministic router in front of this contract:

```text
user text
  -> IntentRouter.parse_text()
  -> IntentResult
  -> IntentRouter.to_action_candidate()
  -> ActionCandidate
  -> PermissionManager.decide()
  -> PermissionDecision
```

Rules:

- No LLM call is required.
- No Ollama dependency is required.
- Unknown text stays unknown or clarification-only.
- Blocked phrasing may still produce blocked `ActionCandidate` for safe preview.
- Conversation/status requests may remain no-action read-only paths.

## Clarification Contract

Ambiguous commands produce `ClarificationRequest` instead of `ActionCandidate`.

| Field | Purpose |
|---|---|
| `reason` | Why clarification is needed |
| `missing_fields` | Required fields not known |
| `candidate_targets` | Possible targets |
| `suggested_questions` | Questions the assistant may ask |
| `safe_default` | Must be `no_action` |

Example:

```text
User: "Isigi ac"
Missing: room, device_id
Assistant: "Hangi isigi acmami istersin? Salon, calisma odasi veya yatak odasi?"
Safe default: no_action
```

## Adapter Execution Boundary

Adapters are future execution components. Sprint 37 defines only their input/output contract.

Rules:

- Adapters accept only approved actions.
- Adapters do not classify natural language.
- Adapters do not override permission decisions.
- Blocked actions never reach adapters.
- Medium/high actions require `ActionPreview` and confirmation first.
- Adapter results must become `ActionResult`.

## Sprint 37/38 Non-Execution Rule

Sprint 37 and Sprint 38 do not implement:

- PC control execution.
- Home/device execution.
- Windows app launch.
- PowerShell or terminal executor.
- STT/TTS/wake word runtime.
- Conversation loop.
- File delete/move/run execution.
- New CLI execution command.
- Adapter calls from PermissionManager.

## Sprint Dependencies

| Dependency | Why it matters |
|---|---|
| Sprint 38 - PermissionManager & Action Approval Flow | Completed non-executing preview and permission decisions |
| Sprint 39 - IntentRouter MVP | Completed deterministic text-to-intent and candidate preview routing |
| Sprint 40 - PC Control Adapter MVP | Executes only approved low/safe PC actions |
| Sprint 43 - RoutineEngine MVP | Uses action preview and risk aggregation |
| Sprint 47 - Home Control Adapter Design | Depends on DeviceRegistry, room model, and approval policy |
