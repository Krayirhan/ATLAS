from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.actions.risk import RiskLevel


class DeviceType(str, Enum):
    LIGHT = "light"
    THERMOSTAT = "thermostat"
    PLUG = "plug"
    SPEAKER = "speaker"
    COMPUTER = "computer"
    SENSOR = "sensor"
    LOCK = "lock"
    CAMERA = "camera"
    UNKNOWN = "unknown"


class DeviceCapabilityType(str, Enum):
    POWER = "power"
    BRIGHTNESS = "brightness"
    TEMPERATURE = "temperature"
    MODE = "mode"
    STATE_QUERY = "state_query"
    VOLUME = "volume"
    MEDIA_CONTROL = "media_control"
    LOCK = "lock"
    CAMERA_STREAM = "camera_stream"
    UNKNOWN = "unknown"


class DeviceRegistryStatus(str, Enum):
    FOUND = "found"
    LISTED = "listed"
    UNRESOLVED = "unresolved"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"
    BLOCKED = "blocked"
    PLANNED = "planned"
    ERROR = "error"


class DeviceSource(str, Enum):
    BUILT_IN = "built_in"
    USER_DEFINED = "user_defined"
    MEMORY = "memory"
    IMPORT_FILE = "import_file"
    HOME_ADAPTER_FUTURE = "home_adapter_future"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class DeviceCapability:
    capability: DeviceCapabilityType
    supported: bool
    readable: bool
    writable: bool
    risk_level: RiskLevel
    requires_confirmation: bool
    parameters_schema: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DeviceState:
    device_id: str
    online: bool = True
    power_state: str = "unknown"
    brightness: int | None = None
    temperature: int | None = None
    mode: str = ""
    last_seen: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RoomDefinition:
    room_id: str
    display_name: str
    aliases: list[str] = field(default_factory=list)
    floor: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DeviceDefinition:
    device_id: str
    display_name: str
    device_type: DeviceType
    room_id: str
    aliases: list[str] = field(default_factory=list)
    capabilities: list[DeviceCapability] = field(default_factory=list)
    state: DeviceState | None = None
    source: DeviceSource = DeviceSource.BUILT_IN
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DeviceAlias:
    alias: str
    device_id: str
    confidence: float = 1.0
    source: DeviceSource = DeviceSource.BUILT_IN
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RoomAlias:
    alias: str
    room_id: str
    confidence: float = 1.0
    source: DeviceSource = DeviceSource.BUILT_IN
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DeviceTargetResolution:
    raw_text: str
    resolved: bool
    device: DeviceDefinition | None = None
    room: RoomDefinition | None = None
    candidates: list[DeviceDefinition] = field(default_factory=list)
    ambiguity_reason: str = ""
    requires_clarification: bool = False
    confidence: float = 0.0
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DeviceActionPlan:
    action_id: str
    action_type: str
    target_device_id: str = ""
    target_room_id: str = ""
    capability: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.LOW
    requires_confirmation: bool = False
    supported: bool = False
    safe_to_preview: bool = True
    safe_to_execute: bool = False
    blocked: bool = False
    blocked_reason: str = ""
    clarification_required: bool = False
    summary: str = ""
    warnings: list[str] = field(default_factory=list)
    audit_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DeviceRegistryResult:
    status: DeviceRegistryStatus
    message: str
    device: DeviceDefinition | None = None
    room: RoomDefinition | None = None
    devices: list[DeviceDefinition] = field(default_factory=list)
    rooms: list[RoomDefinition] = field(default_factory=list)
    resolution: DeviceTargetResolution | None = None
    plan: DeviceActionPlan | None = None
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
