# ATLAS Permission UX

## Purpose

Permission UX defines how ATLAS explains, previews, confirms, blocks, cancels, and audits actions. Sprint 37 adds the canonical risk and confirmation matrix used by future `PermissionManager` work in Sprint 38.

## Core Rule

No medium, high, blocked, unknown, ambiguous, destructive, privacy-sensitive, or voice-risky action should execute without the correct permission outcome.

## Risk Level to Confirmation Matrix

| Risk level | Example action | Preview | Confirmation | Execution policy |
|---|---|---|---|---|
| `safe_readonly` | `pc.system_info`, `file.search`, `device.state_query` | Optional but preferred | No | Future adapter may read; audit required |
| `low` | `pc.open_app`, `pc.open_folder`, `browser.search`, media control | Optional; required if privacy-sensitive | Usually no | Auto only after later policy; audit required |
| `medium` | `reminder.create`, `routine.run`, `device.turn_on` | Required | Explicit confirm | No execution without user approval |
| `high` | `pc.shutdown`, `device.open_door`, high-impact routine | Required | Explicit confirm + warning | May remain deferred; no execution after timeout |
| `blocked` | `file.delete`, `secret.read`, unrestricted shell | Block explanation only | No | Never execute; suggest safe alternative |
| `ambiguous` | "Isigi ac" with no room/device | Clarification only | No | No action candidate until clarified |
| `unknown` | Unclassified request | None/action-safe answer | No | No action execution |

## Sprint 38 PermissionDecision Status Matrix

| Status | Meaning | Next step |
|---|---|---|
| `safe_readonly` | Read-only action is safe to preview/read in future | Return read-only result path; no adapter execution in Sprint 38 |
| `preview_allowed` | Low-risk action preview is allowed | Future adapter may use this only after explicit implementation |
| `confirmation_required` | Medium/high action needs explicit user approval | Ask confirmation; no adapter call in Sprint 38 |
| `clarification_required` | Ambiguous, unknown, missing target, or low-confidence voice action | Ask a clarification question |
| `denied` | User declined action | Return denied `ActionResult` |
| `blocked` | Policy forbids action | Explain block and suggest safe alternative |
| `cancelled` | User or timeout cancelled flow | Return cancelled `ActionResult` |
| `unknown` | Permission engine cannot classify safely | No execution; require review |

## Low Risk

Examples:

- Read system info.
- Media play/pause.
- Open known app.
- Open known folder.
- File search preview.

Policy:

- Preview optional in early text flows, but still useful for user trust.
- Safe auto-execution can be considered only after later policy and audit hardening.
- Voice-source low-risk actions may use lightweight repeat-back when confidence is low.
- Audit is still required.

## Medium Risk

Examples:

- Create reminder.
- Run routine with non-destructive steps.
- Turn on/off a known device.
- Change brightness.
- Change thermostat setpoint.

Policy:

- Explicit confirmation required.
- Show action target, expected result, and state change.
- Allow cancel.
- No confirmation means no execution.
- Voice-source medium action must repeat the understood action and target.

## High Risk

Examples:

- Put PC to sleep, lock, or shut down.
- Unlock/open a device.
- Disable security device.
- Run high-impact routine.
- Any action that can interrupt work or affect physical safety.

Policy:

- Explicit confirmation required.
- Clear warning required.
- No vague confirmation copy.
- No execution after timeout.
- Early ATLAS versions may defer or block many high-risk actions even with confirmation.

## Blocked

Examples:

- Secret file reading.
- Full disk scan.
- Destructive file delete/overwrite.
- App install/uninstall.
- Registry edit.
- Unrestricted shell execution.
- Credential read.

Policy:

- No execution.
- Do not ask for confirmation as if execution is possible.
- Explain the blocked reason.
- Suggest safe alternative when possible.

Blocked copy examples:

| Situation | User-facing copy |
|---|---|
| File delete | `Bu islem ATLAS MVP'de engelli: dosya silme veri kaybi riski tasir. Dosyayi bulup konumunu gosterebilirim.` |
| Secret read | `Bu istegi calistiramam: secret veya kimlik bilgisi okumak ATLAS policy tarafindan engellenir.` |
| Full disk scan | `Tum diski tarayamam. Belirli bir klasor veya proje kapsami secersen arama onizlemesi yapabilirim.` |
| Unrestricted shell | `Sinirsiz terminal komutu calistiramam. Guvenli, onizlemeli bir action tasarimi gerekir.` |

## Voice-Source Action Rules

Voice commands are treated more conservatively because STT may mishear the target or action.

| Voice action type | Rule |
|---|---|
| `safe_readonly` | May answer/read in future; repeat-back if confidence is low |
| `low` | May require lightweight confirmation when target or confidence is weak |
| `medium` | Must repeat target/action and require explicit confirmation |
| `high` | Must repeat target/action, show warning, and require explicit confirmation |
| `blocked` | Must not execute; explain block |
| `ambiguous` | Ask clarification; safe default is no action |

Sprint 38 runtime contract:

- `source=voice` plus medium/high risk always requires confirmation.
- voice confidence below threshold returns `clarification_required`.
- voice prompt starts with a repeat-back style phrase.
- target must be explicit.
- blocked voice actions remain blocked.

Turkish voice confirmation examples:

| Action | Confirmation copy |
|---|---|
| `device.turn_on` | `Salon isigini acacagim. Onayliyor musun?` |
| `routine.run` | `Calisma modu rutinini baslatacagim. Bu islem ekran ve cihaz ayarlarini degistirebilir. Onayliyor musun?` |
| `pc.shutdown` | `Bilgisayari kapatma istegi algiladim. Bu calismanizi kesebilir. Gercekten kapatmak istiyor musun?` |
| `device.set_temperature` | `Salon termostatini 22 dereceye ayarlayacagim. Onayliyor musun?` |

## Ambiguous Intent Rules

Ambiguous intent does not create an executable action.

Rules:

- If room is missing for a device action, ask which room.
- If device alias maps to multiple devices, ask which device.
- If folder name maps to multiple folders, show candidates.
- If command could mean media, app, or device action, ask user to choose.
- If confidence is below threshold, ask a clarification question or answer safely.
- Safe default is always `no_action`.

Clarification copy examples:

| User command | Response |
|---|---|
| `Isigi ac` | `Hangi isigi acmami istersin? Salon, calisma odasi veya yatak odasi?` |
| `Klasoru ac` | `Hangi klasoru acmami istersin? Belgeler, Indirilenler veya proje klasoru?` |
| `Sesi ayarla` | `Sesi hangi seviyeye ayarlayayim?` |
| `Rutini baslat` | `Hangi rutini baslatmamı istersin? Calisma modu, oyun modu veya uyku modu?` |

## Confirmation Channels

| Channel | Status | Notes |
|---|---|---|
| CLI | Foundation | Can show preview and ask manual confirmation in future |
| Desktop panel | Future | Preferred for PC/home actions |
| Voice confirmation | Future | Must handle misrecognition, timeout, and cancel |
| Mobile confirmation | Future | Requires secure bridge and authentication |

## Confirmation Prompt Requirements

Prompts must show:

- action type
- target
- risk level
- expected result
- state change
- reversibility
- warnings
- confirmation choices
- cancel option

No prompt should hide the concrete target behind vague wording.

Turkish prompt examples:

| Risk | Prompt |
|---|---|
| medium | `Hatirlatici olusturulacak: yarin 09:00 - ilac. Onayliyor musun?` |
| medium | `Salon isigini acacagim. Bu fiziksel cihaz durumunu degistirir. Onayliyor musun?` |
| high | `Bilgisayari uyku moduna alacagim. Devam eden isler etkilenebilir. Onayliyor musun?` |
| blocked | `Bu islem engelli: registry degisikligi ATLAS tarafindan calistirilmaz.` |

## Timeout and Cancel

Rules:

- Pending confirmation expires.
- Expired confirmation cancels the action.
- User can cancel at any point before execution.
- Stale pending action cannot be confirmed by an unrelated later utterance.
- New command should clear or explicitly supersede pending confirmation.

## Irreversible Action Policy

Irreversible or hard-to-undo actions are high or blocked by default.

Examples:

- Delete file.
- Overwrite file.
- Shutdown.
- Install/uninstall.
- Registry edit.
- Device action with physical consequence.

Early ATLAS versions should keep destructive actions blocked, not merely high-risk.

## Audit Trail

Every permission decision records:

- raw user goal
- interpreted intent
- interpreted action
- source channel
- confidence
- target
- risk level
- preview
- decision
- confirmation channel
- confirmation status
- adapter selected
- result status
- timestamp
- `execution_attempted=false`

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

## ToolApprovalAgent vs PermissionManager

These systems share the same security philosophy but are not the same layer.

| Layer | Scope | Current role |
|---|---|---|
| `ToolApprovalAgent` / `app/approval` | Devtools command/file/tool/git/MCP-style preview | Read-only support subsystem; no command execution |
| `PermissionManager` / `app/actions` | Personal assistant actions such as PC, browser, routine, and device candidates | Non-executing preview, confirmation, clarification, block, and audit metadata |

## Sprint 38 Status

Sprint 38 turns this UX contract into `PermissionManager & Action Approval Flow`. It still avoids real PC/home execution. Sprint 39 should feed this layer through `IntentRouter` output.
