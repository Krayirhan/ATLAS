# ATLAS - Next Sprints

## Completed Foundation

- **Sprint 25:** V1 RC documentation and usage guide.
- **Sprint 26:** Test coverage hardening.
- **Sprint 27:** Report depth, `audit v1-rc` polish, integration partition.
- **Sprint 27.5:** AI documentation, NotebookLM workflow, context contract, prompt policy, Ollama plan, security boundaries.
- **Sprint 28:** Ollama AI Layer Foundation + read-only `ai ask`.
- **Sprint 28.6:** Ollama warm-up, keep-alive, timeout hardening, context visibility.
- **Sprint 29:** MemoryAgent + ProjectQAAgent Alpha.
- **Sprint 30:** PlannerAgent Alpha.
- **Sprint 31:** CodeReviewerAgent Alpha.
- **Sprint 32:** ToolApproval Design.
- **Sprint 33:** MainAgent Alpha.
- **Sprint 34:** SecurityAuditorAgent.
- **Sprint 35:** DocumentationAgent.
- **Sprint 36:** Product Realignment & Assistant Architecture.
- **Sprint 37:** Action Architecture & Intent Schema.
- **Sprint 38:** PermissionManager & Action Approval Flow.
- **Sprint 39:** IntentRouter MVP.
- **Sprint 40:** PC Control Adapter MVP.
- **Sprint 41:** ConversationLoop MVP.
- **Sprint 42:** Personal Memory & Preferences.
- **Sprint 43:** RoutineEngine MVP.
- **Sprint 44:** Voice Core Architecture.
- **Sprint 45:** STT/TTS MVP.
- **Sprint 46:** DeviceRegistry + Room Model.
- **Sprint 47:** Home Control Adapter Design.
- **Sprint 48:** Desktop Tray / Permission Panel.
- **Sprint 49:** Notification / Reminder / Calendar Assistant.

## Sprint 36 - Completed

**Amac:** ATLAS product direction'i personal control assistant hedefiyle yeniden hizalamak.

**Sonuc:**

- README and KB product direction updated.
- Completed core / parked devtools / missing personal layers separation documented.
- Assistant, action, permission, voice, PC control, home control, and personal memory architecture docs created.
- Developer-agent roadmap parked.

## Sprint 37 - Completed

**Amac:** Assistant commands icin canonical intent ve action modelini tanimlamak.

**Tamamlanan kapsam:**

- Intent category list.
- Canonical `IntentResult` fields.
- Canonical `ActionCandidate` fields.
- Action source values.
- Action type inventory by risk group.
- Risk model: `safe_readonly`, `low`, `medium`, `high`, `blocked`.
- Dry-run / `ActionPreview` contract.
- `ActionResult` status contract.
- `ClarificationRequest` model.
- Ambiguous intent fallback rules.
- 90 Turkish command examples in `32-intent-action-schema.md`.
- Schema-only `app/actions` package and unit tests.

**Kapsam disi kalanlar:**

- PC control execution.
- Home/device execution.
- Windows app launch implementation.
- Voice/STT/TTS/wake word runtime.
- Conversation loop implementation.
- Adapter execution.
- New CLI execution command.

**Acceptance criteria status:**

- Intent and action schema are defined.
- Unknown/ambiguous/blocked inputs do not produce executable actions.
- Medium/high actions require confirmation by contract.
- Blocked actions are non-executable by contract.

## Parked Developer Roadmap

The former near-term developer roadmap remains parked:

- IntegrationAgent as a generic devtools integration agent.
- TestWriterAgent.
- BugFixAgent.
- CodeBuilderAgent.
- RefactorAgent.
- Git Hygiene & Line Ending Policy as near-term product priority.
- V2 Tool Execution Approval as developer tool execution beta.

`IntegrationAgent` can return only if it is re-scoped as Device/Service Integration for personal assistant use. Tool execution approval returns as personal Action Approval, not autonomous developer execution.

## Sprint 38 - Completed

**Amac:** ToolApproval foundation'i personal action approval sistemine evriltmek.

**Tamamlanan kapsam:**

- `ActionCandidate` to `ActionPreview` flow.
- Risk to confirmation matrix implementation.
- Medium/high confirmation contract.
- Blocked action handling.
- Deny/cancel result states.
- Audit metadata for permission decisions.
- confirm/deny/cancel ActionResult modeling.
- voice-source stricter confirmation and low-confidence clarification.
- `33-permission-manager-flow.md`.
- `tests/test_permission_manager.py`.

**Kapsam disi kalanlar:**

- Real PC control execution.
- Home/device execution.
- Desktop panel implementation.
- Voice confirmation runtime.
- Autonomous developer tool execution.

**Acceptance criteria status:**

- Medium risk explicit confirm ister.
- High risk clear warning ister.
- Blocked action calismaz and cannot reach adapters.
- Ambiguous action produces clarification, not approval.
- Voice-originated risky action has stricter confirmation rule.
- Permission decision emits audit-ready metadata.
- `execution_attempted=false` is present in audit metadata.

## Sprint 39 - Completed

**Amac:** User input'i structured `IntentResult`'a ceviren deterministic MVP routing ve permission preview entegrasyonunu yapmak.

**Kapsam:**

- Text command classification.
- Confidence model.
- Entity extraction basics.
- Intent -> `ActionCandidate` mapping.
- PermissionManager preview integration.
- Ambiguous command fallback.
- Unknown/blocked routing.
- `ai intent` CLI preview command.
- Router and CLI tests.

**Kapsam disi:**

- STT.
- PC adapter execution.
- Home/device execution.
- MainAgent route mutation.

**Acceptance criteria:**

- IntentRouter unknown/ambiguous komutu guvenli clarification veya no-action path'ine indirir.
- Intent categories match Sprint 37 schema.
- PermissionManager preview integration calisir.
- `ai intent` execution yapmaz.

## Sprint 40 - Completed

**Amac:** Windows icin safe PC control adapter MVP'sini tasarlamak ve implementasyona baslamak.

**Kapsam:**

- App open.
- Folder open.
- System info.
- Media play/pause.
- Volume control.
- Browser search.
- File search preview.
- Adapter-level dry-run and result contract.

**Kapsam disi:**

- Delete file.
- Shutdown execution.
- Install/uninstall app.
- Registry edit.
- Admin commands.
- Unrestricted shell execution.

**Acceptance criteria:**

- Her MVP action risk, dry-run, approval, and test approach ile tanimlidir.
- Destructive actions blocked/deferred listesinde kalir.
- Adapter accepts only approved actions.

## Sprint 41 - Completed

**Amac:** Text-first conversation loop ve future voice loop davranisini tasarlamak.

**Kapsam:**

- Session state.
- Cancel/interrupt.
- Confirmation turn.
- Stale confirmation prevention.
- Result response.
- Fallback to text.

**Kapsam disi:**

- Wake word.
- TTS runtime.
- Home action execution.

**Acceptance criteria:**

- User can cancel before execution.
- Confirmation turn stale action'a baglanmaz.
- New command cannot accidentally confirm old action.

## Sprint 42 - Completed

**Amac:** Personal memory modelini privacy-first sekilde tanimlamak.

**Kapsam:**

- Preferences.
- Device aliases.
- Room names.
- Routine definitions.
- Safe command history summaries.
- Forget/delete.

**Kapsam disi:**

- Raw log ingestion.
- Browser profile read.
- Secret storage.

**Acceptance criteria:**

- Sensitive memory policy tanimli.
- Forget/delete akisi tanimli.
- Memory writes require policy and audit.

## Sprint 43 - Completed

**Amac:** Repeated personal workflows icin routine definition ve preview modelini tasarlamak.

**Kapsam:**

- Calisma modu.
- Oyun modu.
- Uyku modu.
- Toplanti modu.
- Evden cikiyorum.
- Eve geldim.
- Schedule basics.
- Child-action risk aggregation.

**Kapsam disi:**

- Home device write execution without registry and permission.
- Complex conditional automations.

**Acceptance criteria:**

- Routine preview mandatory.
- Medium/high routine steps confirmation ister.
- High-impact routines are high risk.

## Sprint 44 - Completed

**Amac:** Voice layer'i implementasyon oncesi privacy ve architecture seviyesinde tanimlamak.

**Kapsam:**

- Push-to-talk first.
- Wake word later.
- STT/TTS options.
- Turkish quality.
- Latency targets.
- Privacy rules.
- Voice-source risk escalation.

**Kapsam disi:**

- STT/TTS code.
- Wake word runtime.
- Home action execution.

**Acceptance criteria:**

- Always-listening risk documented.
- Text fallback documented.
- Medium/high voice actions require repeated confirmation.

## Sprint 45 - Completed

**Amac:** Voice MVP icin adapter secimi ve minimum acceptance testlerini hazirlamak.

**Kapsam:**

- Offline/local-first STT candidates.
- TTS candidates.
- Turkish command test set.
- Latency baseline.
- Push-to-talk flow.

**Kapsam disi:**

- Wake word.
- Home action execution.

**Acceptance criteria:**

- Basit Turkish commands icin test matrix hazir.
- Riskli command confirmation path'i voice kaynakli komutlarda zorunlu.

## Sprint 46 - Completed

**Amac:** Home/device control icin canonical device registry, room model, alias resolution, capability matrix, and target clarification altyapisini tamamlamak.

**Kapsam:**

- `app/devices` package
- in-memory `DeviceRegistry`
- room model
- device alias / room alias
- capability matrix
- `DeviceTargetResolver`
- `DeviceActionPlanner`
- `ai device` CLI
- ConversationLoop device clarification improvements

**Kapsam disi:**

- physical device write
- Home Assistant / MQTT
- network discovery
- home adapter runtime

**Acceptance criteria:**

- `Salon isigini ac` resolved + confirmation required.
- `Isigi ac` ambiguous + clarification required.
- `Klimayi 24 derece yap` resolved + confirmation required.
- Kamera/kapi tarzı hedefler blocked veya unsupported.
- No physical device execution.

## Sprint 47 - Completed

**Amac:** Device preview katmanini preview-first home adapter contract'ina baglamak.

**Kapsam:**

- `app/home` package
- `HomeControlAdapter` contract
- `MockHomeControlAdapter`
- `HomeControlPlan` / `HomeControlResult`
- state-read vs state-write boundary
- `DeviceActionPlan -> HomeControlPlan` mapping
- `ai home-preview` CLI
- no-network / no-execution safety tests

**Kapsam disi:**

- Home Assistant client
- MQTT client
- physical device control
- network discovery
- cloud providers

**Acceptance criteria:**

- `Salon isigini ac` home preview + confirmation required.
- `Klimayi 24 derece yap` home preview + confirmation required.
- `Isigi ac` clarification/unsupported.
- no Home Assistant or MQTT runtime.
- no physical device execution.

## Sprint 48 - Completed

**Amac:** Pending confirmation ve blocked/clarification preview akislarini gorunur hale getiren panel backend'ini kurmak.

**Kapsam:**

- `app/panel` package
- panel item / decision / state models
- in-memory + safe local JSON store
- submit/list/show/approve/deny/cancel/clear flows
- `ai panel` CLI
- no-execution approval visibility
- desktop tray UX dokumani

**Kapsam disi:**

- real tray runtime
- GUI framework
- background daemon
- post-approval execution

**Acceptance criteria:**

- submit/list/show works
- approve/deny/cancel model status updates work
- blocked/clarification items cannot be approved
- execution remains disabled

## Sprint 49 - Completed

**Amac:** Local-first reminder / notification / calendar assistant MVP'sini kurmak.

**Tamamlanan kapsam:**

- `app/personal_assistant` package
- reminder models, calendar draft/query models, notification preview models
- local in-memory + safe local JSON store
- `ReminderService`
- `CalendarService`
- `NotificationService`
- `ConversationLoop` reminder/calendar interception
- `PermissionPanelService` reminder/calendar item support
- `ai reminder`
- `ai calendar`
- optional `ai notification-preview`
- local-first privacy / blocked-content policy

**Kapsam disi kalanlar:**

- real OS notification
- background scheduler / daemon
- Google Calendar / Outlook integration
- cloud sync
- email / push notification delivery
- external calendar write

**Acceptance criteria status:**

- reminder create confirmation ister
- calendar draft confirmation ister
- calendar query safe local preview verir
- panel approve real scheduling baslatmaz
- no OS notification / no external calendar / no scheduler boundaries korunur

### Sprint 50 - End-to-End Personal Assistant Demo

**Amac:** Text/voice command'dan permission ve safe PC/routine action sonucuna kadar demo akislarini birlestirmek.

**Kapsam:**

- Text command.
- Optional voice command.
- Intent.
- Action preview.
- Approval.
- Safe PC/routine result.
- Audit.

**Kapsam disi:**

- Unsafe home write actions.
- Autonomous coding.

**Acceptance criteria:**

- En az 5 safe user flow calisir.
- High risk commands execute etmez.

### Sprint 51 - Safety / Latency / UX Hardening

**Amac:** Assistant runtime'i guvenlik, latency ve UX acisindan sertlestirmek.

**Kapsam:**

- Latency budgets.
- Ollama warmup UX.
- Error handling.
- Route regression.
- Action audit completeness.
- Privacy checks.

**Kapsam disi:**

- New feature expansion before hardening.

**Acceptance criteria:**

- Validation suite passes.
- Riskli action confirmation rate is 100%.
- User-visible failure messages are clear.

### Sprint 52 - Safe Execution Gate / Low-Risk PC Execution Planning

**Amac:** Preview-only assistant'tan kontrollu execution kapisina gecis icin low-risk PC execution planini tasarlamak.

**Kapsam:**

- execution gate contract
- low-risk PC action allowlist
- audit and rollback expectations
- panel/confirmation handoff policy

**Kapsam disi:**

- unrestricted shell
- home/device write execution
- reminder scheduler

**Acceptance criteria:**

- execution gate before adapter work is documented
- low-risk PC scope is explicit
- blocked/high-risk boundaries remain unchanged

## V2 / V3 Scope Note

V2 and V3 are no longer developer-agent phases by default. V2 is the personal assistant action/runtime maturity phase. V3 is richer desktop/mobile/home experience after permission, privacy, and adapter safety are stable.
