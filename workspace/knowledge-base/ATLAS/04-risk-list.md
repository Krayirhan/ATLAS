# ATLAS - Risk List

## Highest Active Risks

1. **Preview confused with execution**
   User may think Chrome opened, a light changed, a reminder was scheduled, or a calendar event was written when the system only produced a preview.

2. **Voice misconfirmation**
   A risky voice request may be accepted too casually if low confidence, short confirmation, or stale context are not handled strictly.

3. **Panel approval drift**
   Future code may accidentally treat approve as execution, or allow expired/cancelled/blocked/clarification items to pass.

4. **Execution boundary regression**
   A future adapter or helper may introduce network access, shell usage, microphone capture, scheduler behavior, or physical device writes.

5. **Secret leakage / credential exposure**
   A future memory, docs, logging, or artifact flow may expose secrets, tokens, `.env`-backed values, or credential-like content that must stay unread and unpersisted.

6. **Generated artifact leakage**
   Demo, hardening, report, and state artifacts may look like source deliverables or accidentally enter git.

## Sprint 51 Mitigations

- Central safety invariants now check:
  `execution_attempted`, `physical_device_touched`, `network_used`, `microphone_used`, `wake_word_used`, `audio_retained`, `external_calendar_used`, `os_notification_sent`, `credential_accessed`, `shell_used`
- `ai hardening` measures preview-only safety and latency without opening execution.
- Panel approval now keeps a clear timeout model and blocks approve on expired/cancelled/denied/blocked/clarification items.
- Voice runtime adds stricter confirmation wording and low-confidence clarification behavior.
- CLI copy now repeats preview-only wording in Turkish.
- Demo safety validation now fails on missing safety flags as well as true flags.

## Current Controls

- `PermissionManager` and `IntentRouter` remain preview-only.
- `MainAgent`, `ToolApprovalAgent`, and `SecurityAuditorAgent` remain read-only.
- `MockHomeControlAdapter` keeps `network_used=false`, `physical_device_touched=false`, `execution_attempted=false`.
- Reminder/calendar flows keep `external_calendar_used=false`, `os_notification_sent=false`, `execution_attempted=false`.
- Voice pipeline keeps `microphone_used=false`, `wake_word_used=false`, `audio_retained=false`, `execution_attempted=false`.
- Panel approve records state only and does not start execution.
- Demo runner and hardening suite validate the full safety flag set.

## Remaining Gaps

- Real execution gate does not exist yet.
- Real microphone runtime does not exist yet.
- Real scheduler does not exist yet.
- Real OS notification delivery does not exist yet.
- Real external calendar integration does not exist yet.
- Durable encrypted local state is not implemented.

## Sprint 52 Dependency

Sprint 52 should address bounded execution planning only after:

- safety invariants stay stable
- panel handoff rules are explicit
- low-risk PC allowlist is documented
- audit and rollback expectations are defined
