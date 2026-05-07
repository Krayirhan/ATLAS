# Sprint 46 - DeviceRegistry + Room Model

## Purpose

Sprint 46 adds the canonical identity layer that ATLAS needs before any home automation runtime can exist. This sprint does not control physical devices. It defines devices, rooms, aliases, capabilities, target resolution, and preview-only device action planning.

## Scope

- `app/devices` package
- in-memory `DeviceRegistry`
- room model
- device alias / room alias model
- capability matrix
- `DeviceTargetResolver`
- `DeviceActionPlanner`
- `ai device` CLI
- ConversationLoop integration for device clarification and confirmation-safe previews

## DeviceRegistry Role

`DeviceRegistry` is the canonical source for:

- device ids
- room ids
- friendly names
- aliases
- capability lists
- current demo state

Sprint 46 uses an in-memory demo registry only. There is no discovery, network scan, or external integration.

## Room Model

Room fields:

- `room_id`
- `display_name`
- `aliases`
- `floor`
- `metadata`

Built-in rooms:

- salon
- calisma odasi
- yatak odasi
- mutfak
- koridor

## Device Model

Device fields:

- `device_id`
- `display_name`
- `device_type`
- `room_id`
- `aliases`
- `capabilities`
- `state`
- `source`
- `enabled`
- `metadata`

Built-in demo devices:

- salon isigi
- calisma odasi isigi
- yatak odasi isigi
- salon klimasi
- bilgisayar hoparloru

## Alias Model

Alias support exists at three levels:

1. built-in device aliases
2. built-in room aliases
3. optional read-only personal memory aliases

Sprint 46 does not auto-learn aliases and does not write alias data back into memory.

## Capability Matrix

Examples:

- `device.turn_on` -> `power`
- `device.turn_off` -> `power`
- `device.set_brightness` -> `brightness`
- `device.set_temperature` -> `temperature`
- `device.state_query` -> `state_query`

Blocked / unsupported early classes:

- camera-like privacy actions
- door / unlock style physical-security actions

## Device Target Resolution

`DeviceTargetResolver` supports:

- exact room + device resolution
- alias-based resolution
- candidate listing for ambiguous device-type-only targets
- blocked/unsupported return for risky classes

Examples:

- `Salon isigini ac` -> resolved
- `Ana isigi ac` -> resolved via alias
- `Isigi ac` -> ambiguous, clarification required
- `Klimayi 24 derece yap` -> resolved thermostat target
- `Kamerayi ac` -> blocked/unsupported

## Ambiguous Target Clarification

Ambiguous requests must not create an executable home action.

Example:

```text
User: "Isigi ac"
ATLAS: "Hangi cihazi kastettigini belirtmelisin: Salon Isigi, Calisma Odasi Isigi, Yatak Odasi Isigi."
```

Safe default remains no action.

## PermissionManager Integration

`DeviceActionPlanner` consumes:

- `ActionCandidate`
- `DeviceTargetResolution`
- capability rules
- `PermissionManager`

Expected behavior:

- `device.turn_on/off` -> medium risk, confirmation required
- `device.set_temperature` -> medium risk, confirmation required
- `device.state_query` -> safe read-only
- blocked capability -> blocked plan
- ambiguous target -> clarification-required plan

## ConversationLoop Integration

ConversationLoop now:

- resolves device-like text through `DeviceActionPlanner`
- returns better clarification copy for ambiguous light targets
- keeps device writes preview-only
- does not call any home adapter

## PersonalMemory Alias Integration

Read-only support exists for:

- `device_alias`
- `room_alias`

This is optional and in-memory. Sprint 46 does not create or persist aliases automatically.

## CLI Examples

```powershell
python -m app.cli ai device --project ATLAS --rooms
python -m app.cli ai device --project ATLAS --list
python -m app.cli ai device --project ATLAS "Salon isigini ac"
python -m app.cli ai device --project ATLAS --show-plan "Isigi ac"
python -m app.cli ai device --project ATLAS --json "Klimayi 24 derece yap"
```

## No-Execution Boundary

Sprint 46 still does not add:

- Home Assistant
- MQTT
- network discovery
- cloud device providers
- physical device state writes
- home adapter execution

`safe_to_execute` remains `false`.

## Test Plan

Coverage includes:

- device and room models
- built-in registry listing
- alias resolution
- ambiguous target clarification
- capability validation
- blocked/unsupported device classes
- `ai device` CLI
- ConversationLoop regression

## Acceptance Criteria

- DeviceRegistry exists
- Room model exists
- Device model exists
- Capability matrix exists
- `DeviceTargetResolver` exists
- `DeviceActionPlanner` exists
- `ai device` CLI works
- no physical device execution
- no Home Assistant or MQTT
- no network discovery

## Next Dependency

Sprint 47 should define **Home Control Adapter Design** on top of this registry and target-resolution layer.
