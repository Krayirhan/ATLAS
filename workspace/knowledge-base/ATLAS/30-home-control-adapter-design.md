# ATLAS Home Control Adapter Design

## Purpose

Home control is a later ATLAS capability. This document defines the architecture boundary and safety requirements before any physical device action is implemented.

Sprint 46 completed the prerequisite identity layer:

- canonical device ids
- room model
- alias resolution
- capability matrix
- preview-only device planning
- no real device execution

Sprint 47 completes the contract-level home preview layer, still without real device execution.

## Integration Candidates

| Candidate | Role |
|---|---|
| Home Assistant | First candidate for local-first home control |
| MQTT | Alternative local messaging layer |
| Cloud providers | Later optional integrations after privacy/security review |

Cloud providers are not the default path.

## Dependencies

Home control requires these systems first:

- ActionSchema
- PermissionManager
- DeviceRegistry
- Room Model
- capability model
- state read/write distinction
- audit trail

Sprint 47 now adds:

- `app/home` package
- `HomeControlAdapter` contract
- `MockHomeControlAdapter`
- `HomeControlPlan` / `HomeControlResult`
- `ai home-preview` CLI

## DeviceRegistry Dependency

Each device needs:

- stable device id
- friendly name
- aliases
- room
- capabilities
- current state if available
- integration provider
- safety classification

Ambiguous alias or room names must not produce an executable action.

## Room Model

Room model fields:

- room id
- room name
- aliases
- devices in room
- user-facing description

Examples:

- salon
- calisma odasi
- yatak odasi
- mutfak

## Capability Model

Device capability examples:

- `power`
- `brightness`
- `color`
- `temperature`
- `media`
- `lock`
- `sensor_read`

Actions must match capabilities. A brightness action cannot target a device without brightness capability.

## State Read vs State Write

State read is safer:

- list devices
- read state
- read sensor values
- check online/offline

State write is riskier:

- turn on/off
- set brightness
- set temperature
- unlock/lock
- start appliance

State write requires permission policy and correct device identity.

Sprint 47 boundary:

- state read may return mock/demo read results
- state write remains preview-only
- `safe_to_execute=false`
- no network usage
- no physical device touch

## Approval Policy

| Home action | Default risk | Handling |
|---|---|---|
| read device state | low | allowed after registry exists |
| turn light on/off | medium | confirm in early phase |
| set brightness | medium | confirm in early phase |
| change temperature | high | explicit confirm plus warning |
| lock/unlock | high/blocked | defer until strong policy |
| appliance control | high/blocked | defer |

## Safety Rules

- No physical device action until PermissionManager is ready.
- No physical device action until DeviceRegistry is ready.
- No ambiguous device target execution.
- No cloud provider default.
- No action without audit.
- Voice-originated home write action requires explicit confirmation.
- High-risk device classes remain blocked until separately approved.

## MVP Design Sequence

1. DeviceRegistry.
2. Room Model.
3. HomeControlAdapter contract.
4. Mock home preview adapter.
5. State-read preview path.
6. Action preview for write actions.
7. Confirmation UX.
8. Limited low/medium write actions later.
9. Hardening and audit review.
