# ATLAS Permission UX

## Purpose

Permission UX defines how ATLAS explains, previews, confirms, blocks, and audits actions.

## Core Rule

No medium, high, blocked, unknown, destructive, ambiguous, or voice-risky action should execute without the correct permission outcome.

## Risk Handling

### Low Risk

Examples:

- read system info
- media play/pause
- open known app
- file search preview

Policy:

- preview optional
- safe auto only in later phases
- audit still required

### Medium Risk

Examples:

- open folder with user data
- browser search with personal query
- create reminder
- run routine with non-destructive steps
- device brightness change

Policy:

- explicit confirmation required
- show action target and expected result
- allow cancel

### High Risk

Examples:

- routine with multiple state-changing steps
- device power action
- action that can interrupt work
- action involving privacy-sensitive data

Policy:

- explicit confirmation required
- clear warning required
- no vague confirmation text
- no execution after timeout

### Blocked

Examples:

- secret file reading
- full disk access
- destructive file delete
- shutdown without special policy
- registry edit
- admin command
- home/device write before DeviceRegistry and PermissionManager are ready

Policy:

- no execution
- explain why blocked
- suggest safe alternative if possible

## Confirmation Channels

| Channel | Status | Notes |
|---|---|---|
| CLI | current/foundation | Can show preview and ask manual confirmation in future |
| Desktop panel | future | Preferred for PC/home actions |
| Voice confirmation | future | Must handle misrecognition and timeout |
| Mobile confirmation | future | Requires secure bridge and auth model |

## Irreversible Action Policy

Irreversible or hard-to-undo actions are high or blocked by default.

Examples:

- delete file
- overwrite file
- shutdown
- install/uninstall
- registry edit
- device action with physical consequence

Such actions require a stricter policy and may remain blocked for early assistant versions.

## Voice Misrecognition Policy

Voice-originated actions are treated more conservatively:

- low-risk action can preview or ask lightweight confirmation
- medium/high action must repeat understood target and action
- ambiguous target asks clarification
- no action after silence timeout
- cancel command stops pending action

## Timeout and Cancel

Rules:

- pending confirmation expires.
- expired confirmation cancels action.
- user can cancel at any point before execution.
- stale pending action cannot be confirmed by an unrelated later utterance.

## Audit Trail

Every permission decision records:

- raw user goal
- interpreted action
- source channel
- risk level
- decision
- confirmation channel
- confirmation status
- adapter selected
- result status
- timestamp

## UX Copy Requirements

Permission prompts must show:

- action name
- target
- risk
- expected result
- whether reversible
- confirmation choices
- cancel option

No prompt should hide the concrete target behind vague wording.
