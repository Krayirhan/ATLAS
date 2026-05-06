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

## Sprint 36

### Sprint 36 - Product Realignment & Assistant Architecture

**Amac:** ATLAS product direction'i personal control assistant hedefiyle yeniden hizalamak.

**Kapsam:**

- README ve KB hedef tanimi.
- Completed core / parked devtools / missing personal layers ayrimi.
- Action, assistant, permission, voice, PC control, home control, personal memory docs.
- Developer-agent roadmap'in park edilmesi.

**Kapsam disi:**

- Python app logic.
- Yeni CLI komutu.
- Yeni agent.
- Voice, PC control, home control runtime.

**Acceptance criteria:**

- README yeni product vision'i yansitir.
- `03-current-status.md` uc sinifi gosterir.
- `24`-`31` mimari dokumanlari olusur.
- Final validation komutlari calisir.

## Parked Developer Roadmap

The former near-term roadmap is parked:

- IntegrationAgent as a generic devtools integration agent.
- TestWriterAgent.
- BugFixAgent.
- CodeBuilderAgent.
- RefactorAgent.
- Git Hygiene & Line Ending Policy as near-term product priority.
- V2 Tool Execution Approval as developer tool execution beta.

`IntegrationAgent` can return only if it is re-scoped as Device/Service Integration for personal assistant use. Tool execution approval returns as personal Action Approval, not autonomous developer execution.

## New Personal Assistant Roadmap

### Sprint 37 - Action Architecture & Intent Schema

**Amac:** Assistant commands için canonical intent ve action modelini tanimlamak.

**Kapsam:**

- Intent examples.
- `ActionSchema` fields.
- action types and targets.
- risk fields.
- expected result model.

**Kapsam disi:**

- PC control execution.
- Voice runtime.
- Home/device execution.

**Acceptance criteria:**

- `pc.open_app`, `pc.open_folder`, `browser.search`, `routine.run`, `device.turn_on` gibi action types tanimli.
- Her action risk, confirmation, dry-run, reversible, expected result alanlarini tarif eder.
- Unknown intent default olarak no execution olur.

### Sprint 38 - PermissionManager & Action Approval Flow

**Amac:** ToolApproval foundation'i personal action approval sistemine evriltmek.

**Kapsam:**

- low/medium/high/blocked risk policy.
- confirmation channels.
- irreversible action policy.
- action preview.
- audit metadata.

**Kapsam disi:**

- Gercek action execution.
- Desktop panel implementation.
- Voice confirmation runtime.

**Acceptance criteria:**

- Medium risk explicit confirm ister.
- High risk clear warning ister.
- Blocked action calismaz.
- Voice-originated risky action daha konservatif ele alinir.

### Sprint 39 - IntentRouter MVP

**Amac:** User input'i structured intent'e ceviren MVP routing tasarimini yapmak.

**Kapsam:**

- text command classification.
- confidence model.
- ambiguous command fallback.
- MainAgent relationship.

**Kapsam disi:**

- STT.
- PC adapter execution.

**Acceptance criteria:**

- IntentRouter unknown/ambiguous komutu action'a cevirmez.
- MainAgent, IntentRouter ve ActionRouter sorumluluklari ayrilir.

### Sprint 40 - PC Control Adapter MVP

**Amac:** Windows icin safe PC control adapter MVP'sini tasarlamak ve sonraki implementasyona hazirlamak.

**Kapsam:**

- app open.
- folder open.
- system info.
- media play/pause.
- volume control.
- browser search.
- file search preview.

**Kapsam disi:**

- delete file.
- shutdown.
- install app.
- registry edit.
- admin commands.

**Acceptance criteria:**

- Her MVP action risk, dry-run, approval, test approach ile tanimlidir.
- Destructive actions blocked/deferred listesinde kalir.

### Sprint 41 - ConversationLoop MVP

**Amac:** Text-first conversation loop ve future voice loop davranisini tasarlamak.

**Kapsam:**

- session state.
- cancel/interrupt.
- confirmation turn.
- result response.
- fallback to text.

**Kapsam disi:**

- Wake word.
- TTS runtime.

**Acceptance criteria:**

- User can cancel before execution.
- Confirmation turn stale action'a baglanmaz.

### Sprint 42 - Personal Memory & Preferences

**Amac:** Personal memory modelini privacy-first sekilde tanimlamak.

**Kapsam:**

- preferences.
- device aliases.
- room names.
- routine definitions.
- safe command history summaries.
- forget/delete.

**Kapsam disi:**

- raw log ingestion.
- browser profile read.
- secret storage.

**Acceptance criteria:**

- Sensitive memory policy tanimli.
- Forget/delete akisi tanimli.

### Sprint 43 - RoutineEngine MVP

**Amac:** Repeated personal workflows icin routine definition ve preview modelini tasarlamak.

**Kapsam:**

- calisma modu.
- oyun modu.
- uyku modu.
- toplanti modu.
- evden cikiyorum.
- eve geldim.
- schedule basics.

**Kapsam disi:**

- Home device write execution.
- Complex conditional automations.

**Acceptance criteria:**

- Routine preview mandatory.
- Medium/high risk routine steps confirmation ister.

### Sprint 44 - Voice Core Architecture

**Amac:** Voice layer'i implementasyon oncesi privacy ve architecture seviyesinde tanimlamak.

**Kapsam:**

- push-to-talk first.
- wake word later.
- STT/TTS options.
- Turkish quality.
- latency targets.
- privacy rules.

**Kapsam disi:**

- STT/TTS code.
- Wake word runtime.

**Acceptance criteria:**

- Always-listening risk documented.
- Text fallback documented.

### Sprint 45 - STT/TTS MVP

**Amac:** Voice MVP icin adapter secimi ve minimum acceptance testlerini hazirlamak.

**Kapsam:**

- offline/local-first STT candidates.
- TTS candidates.
- Turkish command test set.
- latency baseline.

**Kapsam disi:**

- Wake word.
- Home action execution.

**Acceptance criteria:**

- Basit Turkish commands icin test matrix hazir.
- Riskli command confirmation path'i voice kaynakli komutlarda zorunlu.

### Sprint 46 - DeviceRegistry + Room Model

**Amac:** Home/device control icin kimlik, oda ve capability modelini hazirlamak.

**Kapsam:**

- device id.
- aliases.
- room names.
- capability model.
- state read/write distinction.

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
- cloud providers later.
- state read before write.
- approval rules.

**Kapsam disi:**

- Physical device runtime execution.
- Cloud account binding.

**Acceptance criteria:**

- No physical device action until PermissionManager and DeviceRegistry are ready.

### Sprint 48 - Desktop Tray / Permission Panel

**Amac:** Local desktop UX icin permission panel, status, logs ve settings tasarimini yapmak.

**Kapsam:**

- tray status.
- pending action panel.
- confirm/cancel.
- audit view.
- settings.

**Kapsam disi:**

- Full dashboard product.
- Mobile bridge.

**Acceptance criteria:**

- Riskli action kullaniciya net preview ile gorunur.
- Cancel path always visible.

### Sprint 49 - Notification / Reminder / Calendar Assistant

**Amac:** Local-first reminder and notification assistant layer'ini tasarlamak.

**Kapsam:**

- reminder.create.
- notification summary.
- local schedule.
- future calendar adapter boundary.

**Kapsam disi:**

- Cloud calendar sync by default.
- Email reading.

**Acceptance criteria:**

- Reminder actions have confirmation when needed.
- Personal data policy documented.

### Sprint 50 - End-to-End Personal Assistant Demo

**Amac:** Text/voice command'dan permission ve safe PC/routine action sonucuna kadar demo akislarini birlestirmek.

**Kapsam:**

- text command.
- optional voice command.
- intent.
- action preview.
- approval.
- safe PC/routine result.
- audit.

**Kapsam disi:**

- Unsafe home write actions.
- Autonomous coding.

**Acceptance criteria:**

- En az 5 safe user flow calisir.
- High risk commands execute etmez.

### Sprint 51 - Safety / Latency / UX Hardening

**Amac:** Assistant runtime'i guvenlik, latency ve UX acisindan sertlestirmek.

**Kapsam:**

- latency budgets.
- Ollama warmup UX.
- error handling.
- route regression.
- action audit completeness.
- privacy checks.

**Kapsam disi:**

- New feature expansion before hardening.

**Acceptance criteria:**

- Validation suite passes.
- Riskli action confirmation rate is 100%.
- User-visible failure messages are clear.

## V2 / V3 Scope Note

V2 and V3 are no longer developer-agent phases by default. V2 is the personal assistant action/runtime maturity phase. V3 is richer desktop/mobile/home experience after permission, privacy, and adapter safety are stable.
