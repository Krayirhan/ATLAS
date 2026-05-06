# Sprint 37 - Intent and Action Schema

## Purpose

This document defines the canonical Sprint 37 intent and action schema for ATLAS as a local-first personal control assistant. It is a documentation and contract artifact. It does not authorize real PC control, home control, voice runtime, terminal execution, or adapter execution.

## Design Status

| Area | Status |
|---|---|
| Intent category list | Defined |
| Action type list | Defined |
| Risk model | Defined |
| Dry-run / preview contract | Defined |
| Action result contract | Defined |
| Clarification model | Defined |
| Turkish example matrix | Defined |
| Real execution | Not implemented |
| Adapter implementation | Not implemented |

## Intent Model

Intent answers: "What type of request is the user making?"

| Field | Required | Purpose |
|---|---:|---|
| `intent_id` | Yes | Unique intent instance id |
| `category` | Yes | Canonical category |
| `confidence` | Yes | 0.0-1.0 confidence |
| `language` | Yes | User command language, usually `tr` first |
| `raw_text` | Yes | Original user message |
| `normalized_text` | Yes | Normalized text for routing |
| `entities` | Yes | Extracted app, folder, room, device, value, time, query |
| `target` | Optional | Primary target if known |
| `action_candidate` | Optional | Proposed action type if unambiguous |
| `ambiguity_reason` | Optional | Why clarification is needed |
| `requires_clarification` | Yes | True when action must not be produced yet |
| `safety_notes` | Yes | Safety, privacy, confidence, and policy notes |

## Intent Categories

| Category | Description |
|---|---|
| `conversation.question` | General answer-only question |
| `conversation.status` | Assistant/project/system status question |
| `personal.memory_query` | Query personal memory or preferences |
| `personal.preference_set` | Store or update a user preference |
| `pc.open_app` | Open known Windows application |
| `pc.open_folder` | Open known folder |
| `pc.system_info` | Read local system information |
| `pc.media_control` | Play, pause, next, previous media |
| `pc.volume_control` | Set or toggle volume |
| `browser.search` | Search/open browser query |
| `file.search` | Search files and show preview |
| `routine.create` | Define routine |
| `routine.run` | Run routine |
| `routine.preview` | Preview routine |
| `reminder.create` | Create reminder |
| `calendar.query` | Read calendar information |
| `device.state_query` | Read device state |
| `device.turn_on` | Turn device on |
| `device.turn_off` | Turn device off |
| `device.set_brightness` | Set brightness |
| `device.set_temperature` | Set temperature |
| `unknown` | Cannot classify safely |
| `ambiguous` | Missing or conflicting target/action |
| `blocked` | Forbidden action request |

Power-control action types such as `pc.sleep`, `pc.lock`, and `pc.shutdown` are included in the action inventory for risk modeling, but Sprint 37 does not add a dedicated power-control intent category. Sprint 39 must decide whether to add a dedicated category or keep these actions unsupported until a later policy.

## Action Model

Action answers: "What would ATLAS do if the request is valid and approved?"

| Field | Required | Purpose |
|---|---:|---|
| `action_id` | Yes | Unique action id |
| `action_type` | Yes | Namespaced action type |
| `target` | Yes | Concrete target |
| `parameters` | Yes | Structured parameter object |
| `source` | Yes | `text`, `voice`, `routine`, `schedule`, `main_agent`, `manual`, `unknown` |
| `user_goal` | Yes | Original user goal |
| `intent_category` | Yes | Source intent category |
| `risk_level` | Yes | `safe_readonly`, `low`, `medium`, `high`, or `blocked` |
| `requires_confirmation` | Yes | Explicit confirmation requirement |
| `dry_run_supported` | Yes | Whether preview can run without state change |
| `reversible` | Yes | Whether undo is possible |
| `expected_result` | Yes | Expected human-readable outcome |
| `blocked_reason` | Required if blocked | Why execution is not allowed |
| `confirmation_prompt` | Required for medium/high UX | Prompt copy |
| `audit_metadata` | Yes | Routing, confidence, policy, timestamp metadata |

## Action Type List

### Safe Read-Only

- `pc.system_info`
- `file.search`
- `device.state_query`
- `calendar.query`
- `routine.preview`
- `reminder.preview`

### Low-Risk Safe Action

- `pc.open_app`
- `pc.open_folder`
- `browser.search`
- `pc.media.play_pause`
- `pc.media.next`
- `pc.media.previous`
- `pc.volume.set`
- `pc.volume.mute_toggle`

### Medium-Risk

- `reminder.create`
- `routine.create`
- `routine.run`
- `device.turn_on`
- `device.turn_off`
- `device.set_brightness`
- `device.set_temperature`

### High-Risk

- `pc.sleep`
- `pc.lock`
- `pc.shutdown`
- `device.unlock`
- `device.open_door`
- `device.disable_security`
- `routine.run_high_impact`

### Blocked

- `file.delete`
- `file.overwrite`
- `app.install`
- `app.uninstall`
- `registry.edit`
- `shell.execute_unrestricted`
- `credential.read`
- `secret.read`
- `full_disk_scan`
- `destructive_system_change`

## Risk Model

| Risk | Meaning | Confirmation |
|---|---|---|
| `safe_readonly` | Reads data only and changes no state | No |
| `low` | Low-impact, reversible, or simple local action | Usually no; preview/log |
| `medium` | Changes local state or physical device state | Yes |
| `high` | Can interrupt work, affect safety/privacy, or cause hard-to-undo impact | Yes + warning |
| `blocked` | Forbidden or outside MVP safety policy | No execution |

Risk classification must consider:

- reversibility
- physical-world effect
- system state change
- file/data loss
- privacy exposure
- security or financial effect
- voice-source misrecognition
- confidence
- target ambiguity
- confirmation requirement

## Dry-Run and Preview Model

`ActionPreview` fields:

- `action_id`
- `summary`
- `target`
- `parameters_preview`
- `risk_level`
- `will_change_state`
- `requires_confirmation`
- `reversible`
- `estimated_effect`
- `warnings`
- `safe_to_execute`
- `blocked_reason`
- `requires_clarification`

Rules:

- Medium/high actions cannot execute without preview.
- Voice-source medium/high actions require repeated target/action confirmation.
- Ambiguous target does not produce an action.
- Ambiguous/unknown preview sets `requires_clarification=true`.
- Blocked action preview only explains why it is blocked.
- Preview must not perform state-changing behavior.

## ActionResult Model

`ActionResult` fields:

- `action_id`
- `status`
- `executed`
- `dry_run`
- `message`
- `result_data`
- `error_code`
- `error_message`
- `audit_metadata`
- `started_at`
- `finished_at`

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

Sprint 37 defines the contract only; real adapter results are future work.

## PermissionDecision Model

Sprint 38 adds this permission decision model:

- `action_id`
- `status`
- `risk_level`
- `allowed_to_execute`
- `requires_confirmation`
- `requires_clarification`
- `blocked`
- `reason`
- `confirmation_prompt`
- `warnings`
- `audit_metadata`
- `next_step`

Status values:

- `safe_readonly`
- `preview_allowed`
- `confirmation_required`
- `clarification_required`
- `denied`
- `blocked`
- `cancelled`
- `unknown`

`execution_attempted` must always be `false` in Sprint 38 audit metadata.

## Clarification Model

`ClarificationRequest` fields:

- `reason`
- `missing_fields`
- `candidate_targets`
- `suggested_questions`
- `safe_default`

Rules:

- `safe_default` must be `no_action`.
- Ambiguous target means no action candidate.
- Clarification questions must name concrete candidate targets when possible.
- If candidates are not known, the assistant asks for the missing field.

Example:

| User | Missing | Assistant |
|---|---|---|
| `Isigi ac` | room, device | `Hangi isigi acmami istersin? Salon, calisma odasi veya yatak odasi?` |

## Permission Matrix

| Risk | Preview | Confirmation | Can reach adapter? |
|---|---|---|---|
| `safe_readonly` | Optional | No | Future read adapter only |
| `low` | Optional | Usually no | Future approved/allowed adapter only |
| `medium` | Required | Yes | Only after approval |
| `high` | Required | Yes + warning | Only after approval; many high actions deferred |
| `blocked` | Block explanation | No | Never |
| `ambiguous` | Clarification | No | Never |
| `unknown` | Safe fallback | No | Never |

Sprint 38 implementation mapping:

| Input | PermissionDecision |
|---|---|
| `safe_readonly` | `safe_readonly` |
| `low` | `preview_allowed` |
| `medium` | `confirmation_required` |
| `high` | `confirmation_required` with warning |
| `blocked` | `blocked` |
| `ambiguous` | `clarification_required` |
| `unknown` | `clarification_required` |
| missing target | `clarification_required` |
| voice + low confidence | `clarification_required` |

## Turkish Intent and Action Examples

This matrix provides example classification targets for Sprint 37. It is not an executable routing table.

| # | Kullanici Komutu | Intent | Action Type | Risk | Confirmation | Not |
|---:|---|---|---|---|---|---|
| 1 | `Chrome'u ac` | `pc.open_app` | `pc.open_app` | `low` | Hayir/preview | Known app |
| 2 | `Spotify'i ac` | `pc.open_app` | `pc.open_app` | `low` | Hayir/preview | Known app |
| 3 | `Not Defteri'ni ac` | `pc.open_app` | `pc.open_app` | `low` | Hayir/preview | Windows app |
| 4 | `VS Code'u ac` | `pc.open_app` | `pc.open_app` | `low` | Hayir/preview | Devtools app but PC action |
| 5 | `Hesap makinesini ac` | `pc.open_app` | `pc.open_app` | `low` | Hayir/preview | Known app |
| 6 | `Belgeler klasorunu ac` | `pc.open_folder` | `pc.open_folder` | `low` | Hayir/preview | Known folder |
| 7 | `Indirilenler klasorunu ac` | `pc.open_folder` | `pc.open_folder` | `low` | Hayir/preview | Known folder |
| 8 | `Masaustu klasorunu ac` | `pc.open_folder` | `pc.open_folder` | `low` | Hayir/preview | Known folder |
| 9 | `ATLAS proje klasorunu ac` | `pc.open_folder` | `pc.open_folder` | `low` | Hayir/preview | Registry target |
| 10 | `Son raporlar klasorunu ac` | `pc.open_folder` | `pc.open_folder` | `low` | Hayir/preview | Known workspace folder |
| 11 | `Bilgisayar durumunu goster` | `pc.system_info` | `pc.system_info` | `safe_readonly` | Hayir | Read-only |
| 12 | `RAM durumunu soyle` | `pc.system_info` | `pc.system_info` | `safe_readonly` | Hayir | Read-only |
| 13 | `Diskte ne kadar yer var` | `pc.system_info` | `pc.system_info` | `safe_readonly` | Hayir | Read-only summary |
| 14 | `Pil durumunu goster` | `pc.system_info` | `pc.system_info` | `safe_readonly` | Hayir | Read-only |
| 15 | `Windows surumunu soyle` | `pc.system_info` | `pc.system_info` | `safe_readonly` | Hayir | Read-only |
| 16 | `Muzigi duraklat` | `pc.media_control` | `pc.media.play_pause` | `low` | Hayir | Media toggle |
| 17 | `Muzigi devam ettir` | `pc.media_control` | `pc.media.play_pause` | `low` | Hayir | Media toggle |
| 18 | `Sonraki sarkiya gec` | `pc.media_control` | `pc.media.next` | `low` | Hayir | Media next |
| 19 | `Onceki sarkiya don` | `pc.media_control` | `pc.media.previous` | `low` | Hayir | Media previous |
| 20 | `Sesi kapat` | `pc.volume_control` | `pc.volume.mute_toggle` | `low` | Hayir | Mute toggle |
| 21 | `Sesi yuzde 30 yap` | `pc.volume_control` | `pc.volume.set` | `low` | Hayir/preview | Numeric value |
| 22 | `Sesi biraz kis` | `pc.volume_control` | `pc.volume.set` | `low` | Hayir/clarify if no step | Relative value |
| 23 | `Sesi yukselt` | `pc.volume_control` | `pc.volume.set` | `low` | Hayir/clarify if no step | Relative value |
| 24 | `Google'da hava durumunu ara` | `browser.search` | `browser.search` | `low` | Hayir/preview | Browser query |
| 25 | `En yakin eczaneyi ara` | `browser.search` | `browser.search` | `low` | Hayir/preview | Location privacy may warn |
| 26 | `Python dataclass nedir ara` | `browser.search` | `browser.search` | `low` | Hayir/preview | Query |
| 27 | `Bugunku haberleri ara` | `browser.search` | `browser.search` | `low` | Hayir/preview | Query |
| 28 | `ATLAS action schema dokumanini bul` | `file.search` | `file.search` | `safe_readonly` | Hayir | File search preview |
| 29 | `Fatura dosyasini ara` | `file.search` | `file.search` | `safe_readonly` | Hayir/preview | Personal filename |
| 30 | `Gecen haftaki raporu bul` | `file.search` | `file.search` | `safe_readonly` | Hayir/preview | Search preview |
| 31 | `Belgeler icinde sozlesme ara` | `file.search` | `file.search` | `safe_readonly` | Hayir/preview | Search preview |
| 32 | `Takvimimde bugun ne var` | `calendar.query` | `calendar.query` | `safe_readonly` | Hayir | Read-only |
| 33 | `Yarin toplantim var mi` | `calendar.query` | `calendar.query` | `safe_readonly` | Hayir | Read-only |
| 34 | `Bu hafta hangi etkinlikler var` | `calendar.query` | `calendar.query` | `safe_readonly` | Hayir | Read-only |
| 35 | `Saat 9'da ilacimi hatirlat` | `reminder.create` | `reminder.create` | `medium` | Evet | Creates reminder |
| 36 | `Yarin faturayi ode diye hatirlat` | `reminder.create` | `reminder.create` | `medium` | Evet | Creates reminder |
| 37 | `Toplantidan 10 dakika once hatirlat` | `reminder.create` | `reminder.create` | `medium` | Evet | Creates reminder |
| 38 | `Bu hatirlaticiyi onizle` | `reminder.create` | `reminder.preview` | `safe_readonly` | Hayir | Preview only |
| 39 | `Calisma modu rutini olustur` | `routine.create` | `routine.create` | `medium` | Evet | Routine definition |
| 40 | `Oyun modu rutini olustur` | `routine.create` | `routine.create` | `medium` | Evet | Routine definition |
| 41 | `Uyku modu rutini olustur` | `routine.create` | `routine.create` | `medium` | Evet | Routine definition |
| 42 | `Toplanti modu rutini olustur` | `routine.create` | `routine.create` | `medium` | Evet | Routine definition |
| 43 | `Calisma modunu baslat` | `routine.run` | `routine.run` | `medium` | Evet | Multi-step possible |
| 44 | `Oyun modunu baslat` | `routine.run` | `routine.run` | `medium` | Evet | Multi-step possible |
| 45 | `Uyku modunu baslat` | `routine.run` | `routine.run` | `medium` | Evet | Multi-step possible |
| 46 | `Toplanti modunu baslat` | `routine.run` | `routine.run` | `medium` | Evet | Multi-step possible |
| 47 | `Calisma modunu onizle` | `routine.preview` | `routine.preview` | `safe_readonly` | Hayir | Preview only |
| 48 | `Eve geldim rutinini onizle` | `routine.preview` | `routine.preview` | `safe_readonly` | Hayir | Preview only |
| 49 | `Salon isigi acik mi` | `device.state_query` | `device.state_query` | `safe_readonly` | Hayir | Read device state |
| 50 | `Mutfak lambasi kapali mi` | `device.state_query` | `device.state_query` | `safe_readonly` | Hayir | Read device state |
| 51 | `Termostat kac derece` | `device.state_query` | `device.state_query` | `safe_readonly` | Hayir | Read device state |
| 52 | `Kapi kilidi durumu ne` | `device.state_query` | `device.state_query` | `safe_readonly` | Hayir | Read device state |
| 53 | `Salon isigini ac` | `device.turn_on` | `device.turn_on` | `medium` | Evet | Physical state change |
| 54 | `Mutfak lambasini ac` | `device.turn_on` | `device.turn_on` | `medium` | Evet | Physical state change |
| 55 | `Calisma odasi lambasini ac` | `device.turn_on` | `device.turn_on` | `medium` | Evet | Physical state change |
| 56 | `Koridor isigini ac` | `device.turn_on` | `device.turn_on` | `medium` | Evet | Physical state change |
| 57 | `Salon isigini kapat` | `device.turn_off` | `device.turn_off` | `medium` | Evet | Physical state change |
| 58 | `Mutfak lambasini kapat` | `device.turn_off` | `device.turn_off` | `medium` | Evet | Physical state change |
| 59 | `Calisma odasi lambasini kapat` | `device.turn_off` | `device.turn_off` | `medium` | Evet | Physical state change |
| 60 | `Koridor isigini kapat` | `device.turn_off` | `device.turn_off` | `medium` | Evet | Physical state change |
| 61 | `Salon isigini yuzde 40 yap` | `device.set_brightness` | `device.set_brightness` | `medium` | Evet | Physical state change |
| 62 | `Calisma odasi isigini yuzde 70 yap` | `device.set_brightness` | `device.set_brightness` | `medium` | Evet | Physical state change |
| 63 | `Yatak odasi isigini kis` | `device.set_brightness` | `device.set_brightness` | `medium` | Evet/clarify value | Missing exact value |
| 64 | `Salon termostatini 22 derece yap` | `device.set_temperature` | `device.set_temperature` | `medium` | Evet | Physical state change |
| 65 | `Klimayi 24 dereceye ayarla` | `device.set_temperature` | `device.set_temperature` | `medium` | Evet | Physical state change |
| 66 | `Oda sicakligini dusur` | `device.set_temperature` | `device.set_temperature` | `medium` | Evet/clarify target/value | Ambiguous target/value |
| 67 | `Bilgisayari uyku moduna al` | `unknown` | `pc.sleep` | `high` | MVP'de execution yok | Power-control category pending |
| 68 | `Bilgisayari kilitle` | `unknown` | `pc.lock` | `high` | MVP'de execution yok | Power-control category pending |
| 69 | `Bilgisayari kapat` | `unknown` | `pc.shutdown` | `high` | MVP'de execution yok | Power-control category pending |
| 70 | `Kapi kilidini ac` | `device.turn_on` | `device.unlock` | `high` | Evet + warning | Likely blocked early |
| 71 | `Garaj kapisini ac` | `device.turn_on` | `device.open_door` | `high` | Evet + warning | Physical safety |
| 72 | `Alarm sistemini devre disi birak` | `device.turn_off` | `device.disable_security` | `high` | Evet + warning | Security impact |
| 73 | `Evden cikiyorum rutinini baslat` | `routine.run` | `routine.run_high_impact` | `high` | Evet + warning | Multi-device impact |
| 74 | `Dosyayi sil` | `blocked` | `file.delete` | `blocked` | Yok | Destructive |
| 75 | `Bu belgeyi uzerine yaz` | `blocked` | `file.overwrite` | `blocked` | Yok | Data loss |
| 76 | `Su uygulamayi kur` | `blocked` | `app.install` | `blocked` | Yok | Install blocked |
| 77 | `Bu programi kaldir` | `blocked` | `app.uninstall` | `blocked` | Yok | Uninstall blocked |
| 78 | `Registry ayarini degistir` | `blocked` | `registry.edit` | `blocked` | Yok | System risk |
| 79 | `Herhangi bir PowerShell komutunu calistir` | `blocked` | `shell.execute_unrestricted` | `blocked` | Yok | Unrestricted shell |
| 80 | `.env dosyasini oku` | `blocked` | `secret.read` | `blocked` | Yok | Secret access |
| 81 | `SSH anahtarimi goster` | `blocked` | `credential.read` | `blocked` | Yok | Credential access |
| 82 | `Tum diski tara` | `blocked` | `full_disk_scan` | `blocked` | Yok | Scope/privacy risk |
| 83 | `Sistem dosyalarini temizle` | `blocked` | `destructive_system_change` | `blocked` | Yok | Destructive system |
| 84 | `Isigi ac` | `ambiguous` | `none` | `none` | Clarification | Missing room/device |
| 85 | `Klasoru ac` | `ambiguous` | `none` | `none` | Clarification | Missing folder |
| 86 | `Sesi ayarla` | `ambiguous` | `none` | `none` | Clarification | Missing value |
| 87 | `Rutini baslat` | `ambiguous` | `none` | `none` | Clarification | Missing routine |
| 88 | `Bunu hatirlat` | `ambiguous` | `none` | `none` | Clarification | Missing content/time |
| 89 | `Ne durumdayiz` | `conversation.status` | `none` | `safe_readonly` | Hayir | Answer-only/status |
| 90 | `ATLAS ne yapabilir` | `conversation.question` | `none` | `safe_readonly` | Hayir | Answer-only |

## Ambiguous Intent Fallback Rules

- If target is missing, ask for target.
- If multiple targets match, list the top safe candidates.
- If action is unclear, ask what the user wants done.
- If confidence is low, do not produce action.
- If source is voice and confidence is low, repeat what was heard and ask for confirmation or clarification.
- Safe default is no action.

## Execution Boundary

Sprint 37 and Sprint 38 have no execution runtime:

- No PC control adapter.
- No home control adapter.
- No Windows app open code.
- No terminal executor.
- No STT/TTS/wake word runtime.
- No conversation loop implementation.
- No file operation execution.
- No adapter code.
- No PermissionManager adapter calls.

The schema and PermissionManager can be tested in isolation and then consumed by Sprint 39 IntentRouter work.
