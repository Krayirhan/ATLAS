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

### Sprint 45 - STT/TTS MVP

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

### Sprint 46 - DeviceRegistry + Room Model

**Amac:** Home/device control icin kimlik, oda ve capability modelini hazirlamak.

**Kapsam:**

- Device id.
- Aliases.
- Room names.
- Capability model.
- State read/write distinction.
- Wrong-target prevention.

**Kapsam disi:**

- Physical device write action.
- Cloud provider integration.

**Acceptance criteria:**

- Ambiguous device alias action'a donusmez.
- Device capability olmadan write action yok.

### Sprint 47 - Home Control Adapter Design

**Amac:** Home Assistant first candidate ve MQTT alternative ile home control tasarimini yapmak.

**Kapsam:**

- Home Assistant first candidate.
- MQTT alternative.
- Cloud providers later.
- State read before write.
- Approval rules.
- Device registry dependency.

**Kapsam disi:**

- Physical device runtime execution before PermissionManager and DeviceRegistry are ready.
- Cloud account binding.

**Acceptance criteria:**

- No physical device action until PermissionManager and DeviceRegistry are ready.

### Sprint 48 - Desktop Tray / Permission Panel

**Amac:** Local desktop UX icin permission panel, status, logs ve settings tasarimini yapmak.

**Kapsam:**

- Tray status.
- Pending action panel.
- Confirm/cancel.
- Audit view.
- Settings.

**Kapsam disi:**

- Full dashboard product.
- Mobile bridge.

**Acceptance criteria:**

- Riskli action kullaniciya net preview ile gorunur.
- Cancel path always visible.

### Sprint 49 - Notification / Reminder / Calendar Assistant

**Amac:** Local-first reminder and notification assistant layer'ini tasarlamak.

**Kapsam:**

- `reminder.create`.
- Notification summary.
- Local schedule.
- Future calendar adapter boundary.

**Kapsam disi:**

- Cloud calendar sync by default.
- Email reading.

**Acceptance criteria:**

- Reminder actions have confirmation when needed.
- Personal data policy documented.

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

## V2 / V3 Scope Note

V2 and V3 are no longer developer-agent phases by default. V2 is the personal assistant action/runtime maturity phase. V3 is richer desktop/mobile/home experience after permission, privacy, and adapter safety are stable.
