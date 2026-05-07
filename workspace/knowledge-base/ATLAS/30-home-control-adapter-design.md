# ATLAS Home Control Adapter Design

## Purpose

Home control is a later ATLAS capability. This document defines the architecture boundary and safety requirements before any physical device action is implemented.

Sprint 46 now completes the prerequisite identity layer:

- canonical device ids
- room model
- alias resolution
- capability matrix
- preview-only device planning
- no real device execution

No home automation runtime is implemented in Sprint 36.

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
3. State read adapter.
4. Action preview for write actions.
5. Confirmation UX.
6. Limited low/medium write actions.
7. Hardening and audit review.
