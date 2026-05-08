# Sprint 47 - Home Control Adapter Design

## Purpose

Sprint 47 adds the contract-level home preview layer that sits on top of Sprint 46 device identity and target resolution. This sprint does not connect to Home Assistant, MQTT, or any physical device.

## HomeControlAdapter Role

`HomeControlAdapter` is the future boundary between approved device-oriented actions and concrete home integrations. In Sprint 47 it exists only as a contract plus a mock implementation.

Current Sprint 47 responsibilities:

- accept a preview-safe `DeviceActionPlan`
- convert it into a `HomeControlPlan`
- separate state-read from state-write
- preserve permission and risk metadata
- produce non-executing results

## Integration Strategy

### Home Assistant first candidate

Home Assistant is the first real adapter candidate because:

- local-first deployment is possible
- entity and state model are mature
- state-read vs state-write is naturally separable
- device abstraction is stronger than vendor-direct APIs
- it fits ATLAS permission and audit boundaries better than ad hoc direct integrations

### MQTT alternative

MQTT remains an alternative, not the default:

- lightweight and local-first
- useful for custom device bridges
- topic design and payload validation are safety-sensitive
- direct publish without permission and capability validation would be too risky

### Cloud providers later

Cloud providers stay out of scope for Sprint 47:

- not default
- privacy and token exposure risks are higher
- must be opt-in only in a later phase

## DeviceRegistry Dependency

Sprint 47 depends on Sprint 46 artifacts:

- canonical `device_id`
- canonical `room_id`
- alias resolution
- capability matrix
- ambiguity detection
- preview-only `DeviceActionPlan`

No home plan should be created from an unresolved or ambiguous target.

## Capability Matrix Dependency

Examples:

- `device.state_query` -> `state_query`
- `device.turn_on` / `device.turn_off` -> `power`
- `device.set_brightness` -> `brightness`
- `device.set_temperature` -> `temperature`

Blocked or unsupported classes remain blocked:

- camera stream
- lock / unlock
- open-door
- disable-security

## State Read vs State Write Boundary

State read:

- safe read-only path
- no confirmation by default
- returns mock/demo state only in Sprint 47

State write:

- medium or higher risk by default
- confirmation required
- remains preview-only in Sprint 47
- no adapter execution and no physical state change

## PermissionManager Dependency

`PermissionManager` remains the authority for:

- risk classification
- confirmation requirement
- blocked decisions
- clarification-only paths

`HomeControlPlanner` must preserve these decisions, not weaken them.

## MockHomeControlAdapter

Sprint 47 includes only `MockHomeControlAdapter`.

Behavior:

- no Home Assistant calls
- no MQTT publish/subscribe
- no network usage
- no physical device touch
- `executed=false`
- `execution_attempted=false`
- `network_used=false`
- `physical_device_touched=false`

## Preview Flow

```text
Text
  -> IntentRouter
  -> DeviceActionPlanner
  -> HomeControlPlanner
  -> MockHomeControlAdapter
  -> HomeControlPlan / HomeControlResult
```

Examples:

- `Salon isigini ac` -> home preview, medium risk, confirmation required
- `Klimayi 24 derece yap` -> home preview, medium risk, confirmation required
- `Isigi ac` -> clarification / unsupported
- `Kamerayi ac` -> blocked / unsupported
- `Salon klimasi acik mi` -> safe read-only state preview

## CLI Examples

```powershell
python -m app.cli ai home-preview --project ATLAS "Salon isigini ac"
python -m app.cli ai home-preview --project ATLAS --show-plan "Klimayi 24 derece yap"
python -m app.cli ai home-preview --project ATLAS --json "Isigi ac"
python -m app.cli ai home-preview --project ATLAS --adapter-status
python -m app.cli ai home-preview --project ATLAS --capabilities
```

## No-Execution Boundary

Sprint 47 still does not add:

- Home Assistant client
- MQTT client
- HTTP requests to devices
- network discovery
- LAN scans
- token or credential loading
- physical device state changes
- background listeners

## Future Real Adapter Requirements

Before any real home adapter is allowed:

- explicit opt-in configuration
- credential handling policy
- adapter-specific health checks
- stale-state and source attribution
- desktop/mobile confirmation UX
- audit completeness
- regression tests proving no unsafe fallback path

## Test Plan

Coverage should prove:

- home models build correctly
- mock adapter stays non-executing
- planner produces write previews and read previews correctly
- ambiguous targets stop before execution
- blocked capabilities remain blocked
- CLI works without network usage

## Acceptance Criteria

- `app/home` exists
- `HomeControlAdapter` contract exists
- `MockHomeControlAdapter` exists
- `HomeControlPlan` and `HomeControlResult` exist
- `ai home-preview` works
- state-read vs state-write boundary is explicit
- Home Assistant is documented as first candidate
- MQTT is documented as alternative
- no network usage
- no physical device execution

## Next Dependency

Sprint 48 now defines **Desktop Tray / Permission Panel** so pending home confirmations can move out of ad hoc CLI-only visibility.

That panel layer must still avoid:

- real execution
- network calls
- silent approval replay
