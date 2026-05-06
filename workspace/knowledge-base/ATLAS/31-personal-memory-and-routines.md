# ATLAS Personal Memory and Routines

## Purpose

Personal memory and routines turn ATLAS from a project-aware assistant into a personal control assistant. This layer must be privacy-first and deletable.

No memory/routine runtime is implemented in Sprint 36.

## Personal Memory Categories

| Category | Examples | Sensitivity |
|---|---|---|
| personal preferences | preferred apps, answer style, notification style | medium |
| device aliases | "masa lambasi", "calisma monitoru" | medium |
| room names | "calisma odasi", "salon" | medium |
| routine definitions | "calisma modu", "uyku modu" | medium/high |
| schedules | reminder times, routine schedules | medium/high |
| command history summaries | safe summarized patterns | medium |

Raw logs, secrets, browser profiles, and private keys are not personal memory.

## Sensitive Memory Policy

Rules:

- No secret values.
- No raw `.env`.
- No raw browser profile.
- No private key or keystore.
- No raw logs with possible tokens.
- Sensitive memory requires category and purpose.
- User must be able to forget/delete stored memory.

## Forget/Delete

Personal memory must support:

- delete preference
- delete device alias
- delete routine
- clear command history summary
- export before delete if user asks
- audit memory deletion without storing deleted secret content

## Export and Backup

Export/backup policy:

- user initiated
- local file only by default
- no cloud upload by default
- sensitive categories marked
- no secret expansion

## Routine Definitions

Routine fields:

- routine id
- name
- aliases
- trigger type
- schedule if any
- action list
- risk level
- confirmation policy
- expected result
- audit metadata

## Routine Examples

### calisma modu

Possible future steps:

- open work apps
- set volume
- open project folder
- set reminder focus timer

Risk: medium if multiple state changes are included.

### oyun modu

Possible future steps:

- open game launcher
- adjust volume
- pause notifications later

Risk: medium.

### uyku modu

Possible future steps:

- reduce volume
- set reminder/alarm later
- future lights off after home control readiness

Risk: medium/high when home devices are included.

### toplanti modu

Possible future steps:

- mute media
- open meeting app
- set status later

Risk: medium.

### evden cikiyorum

Possible future steps:

- checklist
- future device state changes after home permission model

Risk: high when physical devices are included.

### eve geldim

Possible future steps:

- greeting summary
- future device actions after home control readiness

Risk: medium/high when physical devices are included.

## Schedule and Triggers

Supported design targets:

- manual trigger first
- schedule later
- conditional trigger later
- location-based trigger only after mobile bridge security review

## Routine Preview

Before execution, ATLAS must show:

- routine name
- all actions
- targets
- risk levels
- confirmation needs
- expected result
- cancel option

## Command History

Command history should store summaries, not raw sensitive transcripts by default.

Allowed:

- "User often opens browser search after work mode"
- "User prefers text confirmation for PC actions"

Not allowed:

- raw secrets
- private filenames if sensitive
- raw voice transcript containing sensitive info without explicit opt-in

## Privacy Notes

Personal memory is a product feature and a risk surface. Sprint 42 should define storage format, deletion behavior, and sensitivity tags before implementation.
