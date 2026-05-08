# Sprint 50 — End-to-End Personal Assistant Demo

## Sprint 50 Purpose

Sprint 50 connects all ATLAS preview-layer modules built in Sprints 36–49 into a single demonstrable, safe, end-to-end personal assistant flow.

The goal is to show — without any real execution — that the following pipeline works:

```
User text / voice mock
  -> IntentRouter
  -> ActionCandidate + PermissionDecision
  -> PC / Device / Home / Routine / Memory / Reminder / Calendar / Panel preview
  -> Safety validation
  -> Demo report
```

Sprint 50 does not open any real execution boundary.

---

## Demo Scenario List

| # | Scenario ID | Category | Surface | Input Text |
|---|-------------|----------|---------|------------|
| 1 | `chat_chrome_open` | chat | chat | Chrome'u aç |
| 2 | `ambiguous_light` | device | device | Işığı aç |
| 3 | `home_salon_light` | home_preview | home_preview | Salon ışığını aç |
| 4 | `blocked_secret` | safety | chat | Şifrelerimi oku |
| 5 | `routine_work_mode` | routine | routine | Çalışma modunu başlat |
| 6 | `voice_home_preview` | voice | voice | Salon ışığını aç (mock) |
| 7 | `memory_preference_store` | memory | memory_personal | Bunu hatırla: Chrome tarayıcısını sık kullanırım |
| 8 | `memory_sensitive_blocked` | safety | memory_personal | Şifremin 1234 olduğunu hatırla |
| 9 | `reminder_create` | reminder | reminder | Bana 20 dakika sonra su içmeyi hatırlat |
| 10 | `calendar_draft` | calendar | calendar | Yarın 10'a toplantı ekle |
| 11 | `calendar_query` | calendar | calendar | Bugün takvimimde ne var? |
| 12 | `panel_queue_light` | panel | panel | Salon ışığını aç |
| 13 | `home_climate_preview` | home_preview | home_preview | Klimayı 24 derece yap |
| 14 | `notification_preview` | mixed | chat | Su içme zamanı |

---

## ai demo CLI Usage

```bash
# List all available scenarios
python -m app.cli ai demo --project ATLAS --list

# Run a single scenario
python -m app.cli ai demo --project ATLAS --scenario chat_chrome_open

# Run a category
python -m app.cli ai demo --project ATLAS --category voice --show-safety

# Run all scenarios with safety summary
python -m app.cli ai demo --project ATLAS --all --show-safety

# Run all and output as JSON
python -m app.cli ai demo --project ATLAS --all --json

# Run all and output as Markdown (to stdout, no file write)
python -m app.cli ai demo --project ATLAS --all --markdown --no-write

# Run all and write Markdown report to file
python -m app.cli ai demo --project ATLAS --all --markdown \
  --output workspace/outputs/demo/sprint-50-demo.md
```

---

## Expected Demo Flows

### Chat / PC Preview
- User says "Chrome'u aç"
- IntentRouter parses as `pc.open_app`
- PCControlAdapter builds a dry-run plan
- Response type: `action_preview`
- No Chrome opens

### Voice Mock
- Mock STT transcript: "Salon ışığını aç"
- VoicePipeline processes with MockSTTAdapter
- `microphone_used=False`, `wake_word_used=False`, `audio_retained=False`
- Response: device confirmation required

### Blocked Secret
- User says "Şifrelerimi oku"
- IntentRouter or ConversationLoop blocks
- Response type: `blocked`
- No credential read

### Reminder Draft
- User says "Bana 20 dakika sonra su içmeyi hatırlat"
- ReminderService creates a pending confirmation draft
- `os_notification_sent=False`
- No OS scheduler activated

### Calendar Draft
- User says "Yarın 10'a toplantı ekle"
- CalendarService creates a local event draft
- `external_calendar_used=False`
- No Google/Outlook API called

---

## Safety Boundaries

The following execution boundaries are enforced in every demo scenario:

| Safety Flag | Value |
|-------------|-------|
| `execution_attempted` | `False` |
| `physical_device_touched` | `False` |
| `network_used` | `False` |
| `microphone_used` | `False` |
| `wake_word_used` | `False` |
| `audio_retained` | `False` |
| `external_calendar_used` | `False` |
| `os_notification_sent` | `False` |
| `credential_accessed` | `False` |
| `shell_used` | `False` |

All flags are validated by `app/demo/policy.py` (`DemoSafetyPolicy`). Any true flag causes the scenario to fail.

---

## What Works Now

- `app/demo` package with models, scenarios, runner, policy, report
- 14 built-in demo scenarios covering all major preview flows
- `DemoRunner.run_scenario()`, `run_all()`, `run_category()`
- `ai demo --list / --scenario / --category / --all / --json / --markdown / --show-safety / --no-write`
- Markdown and JSON demo report generation
- Output path traversal protection (`workspace/outputs/demo/` only)
- Safety policy validation on every result
- 56 passing tests

---

## What Still Does Not Execute

- Chrome / browser
- Home lights, climate, or any physical device
- OS notifications (Windows/macOS)
- Background reminders or calendar alarms
- Google Calendar / Outlook / Microsoft Graph
- Real STT/TTS engine
- Wake word detection
- Home Assistant / MQTT
- Shell or subprocess execution
- Credential / .env reading

---

## Generated Report Policy

- Reports are generated to `workspace/outputs/demo/` if `--output` is provided.
- The generated artifact is not committed to git.
- `--no-write` suppresses file writing and prints to stdout.
- Output path validation prevents writes outside `workspace/outputs/demo/`.

---

## Test Plan

| File | Coverage |
|------|----------|
| `tests/test_demo_scenarios.py` | Scenario count, unique IDs, safety flag presence, required IDs |
| `tests/test_demo_runner.py` | Each scenario run, run_all, run_category, safety validation |
| `tests/test_ai_demo_cli.py` | CLI --list, --scenario, --all, --json, --markdown, --show-safety, --no-write, regression |

---

## Acceptance Criteria

- [x] `app/demo` package created
- [x] `DemoScenario / DemoResult / DemoReport` models exist
- [x] >= 12 built-in scenarios (14 created)
- [x] `DemoRunner` works
- [x] `ai demo` CLI works
- [x] `--list` works
- [x] `--scenario` works
- [x] `--category` works
- [x] `--all` works
- [x] `--json` works (valid JSON)
- [x] `--markdown --no-write` works
- [x] `chat_chrome_open` passes
- [x] `ambiguous_light` passes
- [x] `blocked_secret` passes
- [x] `voice_home_preview` passes
- [x] `reminder_create` passes
- [x] `calendar_draft` passes
- [x] All scenario safety flags = False
- [x] No real PC execution
- [x] No real home execution
- [x] No real OS notification
- [x] No real calendar API
- [x] No real microphone
- [x] No wake word
- [x] No shell executor
- [x] Generated report not committed
- [x] pytest: 463 passed
- [x] doctor --full: ok
- [x] docs-audit: ok
- [x] security-audit: ok
- [x] audit v1-rc: GO

---

## Sprint 51 Dependency

**Sprint 51 — Safety / Latency / UX Hardening**

- Tighten safety regression suite across all adapters.
- Add latency budgets and measure intent routing latency.
- Improve CLI output clarity for end users (Turkish UX polish).
- Add confirmation timeout / cancel implementation.
- Voice confirmation policy runtime.
- Action audit completeness review.
