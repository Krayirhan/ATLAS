# ATLAS - Risk List

## Highest Active Risks

1. **Preview confused with execution**
   User may think Chrome opened, a light changed, a reminder was scheduled, or a calendar event was written when the system only produced a preview or execution plan.

2. **Execution gate bypass**
   A future helper may bypass `ExecutionGate`, skip allowlist checks, or treat a preview result as if execution were already approved.

3. **Allowlist drift / target spoofing**
   A free-form target, alias mismatch, or injected path may accidentally resolve to an unsupported app or future executable path.

4. **PowerShell/cmd or unrestricted shell creep**
   A future implementation may reintroduce PowerShell, cmd, shell strings, `subprocess`, or arbitrary argument passing under the name of low-risk automation.

5. **Panel approval replay / expired approval execution**
   Old, expired, denied, or cancelled panel items may be replayed into execution handoff if state handling is weak.

6. **Accidental real execution**
   A bug in gate, adapter, or CLI wiring may cross the preview boundary and trigger a real app, file, or system side effect.

7. **Rollback false confidence**
   Users may assume rollback exists operationally when Sprint 52 only defines a rollback contract and metadata shape.

8. **Secret leakage / credential exposure**
   A future memory, docs, logging, or artifact flow may expose secrets, tokens, `.env`-backed values, or credential-like content that must stay unread and unpersisted.

9. **Execution audit gap**
   A missing or partial audit record may hide whether approval, allowlist, or execution-disabled policy actually applied.

10. **Generated artifact leakage**
   Demo, hardening, report, and state artifacts may look like source deliverables or accidentally enter git.

## Sprint 52 Mitigations

- `ExecutionGate` adds a typed policy boundary before any future runtime.
- `execution_enabled=false` remains the default for every execution plan.
- Allowlist planning is limited to canonical low-risk app entries:
  `Chrome`, `Notepad`, `Calculator`, `VS Code`
- PowerShell, cmd, unrestricted shell, destructive file ops, registry edit, secret read, and credential read stay blocked.
- Panel handoff now recognizes approved vs expired/denied/cancelled/blocked item state before execution readiness.
- `ai execution` exposes planning and policy visibility without opening runtime execution.
- Audit metadata keeps `execution_attempted=false`, `shell_used=false`, and `credential_accessed=false`.

## Current Controls

- `PermissionManager` and `IntentRouter` remain preview-only.
- `ExecutionGate.execute()` returns disabled and does not call `subprocess`, `os.startfile`, PowerShell, cmd, or shell.
- `MainAgent`, `ToolApprovalAgent`, and `SecurityAuditorAgent` remain read-only.
- `MockHomeControlAdapter` keeps `network_used=false`, `physical_device_touched=false`, `execution_attempted=false`.
- Reminder/calendar flows keep `external_calendar_used=false`, `os_notification_sent=false`, `execution_attempted=false`.
- Voice pipeline keeps `microphone_used=false`, `wake_word_used=false`, `audio_retained=false`, `execution_attempted=false`.
- Panel approve records state only and does not start execution.
- Demo runner and hardening suite validate the full safety flag set.

## Remaining Gaps

- Real low-risk PC runtime does not exist yet.
- Real home execution does not exist yet.
- Real microphone runtime does not exist yet.
- Real scheduler does not exist yet.
- Real OS notification delivery does not exist yet.
- Real external calendar integration does not exist yet.
- Durable encrypted local state is not implemented.

## Sprint 53 Dependency

Sprint 53 should open only a very narrow low-risk PC execution MVP after:

- Safe Execution Gate invariants stay stable
- allowlist spoofing tests stay green
- panel replay and expiry handling stay explicit
- audit requirements are enforced before runtime
- no unrestricted shell path exists anywhere in the flow
