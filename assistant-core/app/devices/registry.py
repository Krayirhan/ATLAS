from __future__ import annotations

from app.actions.risk import RiskLevel
from app.devices.models import (
    DeviceCapability,
    DeviceCapabilityType,
    DeviceDefinition,
    DeviceSource,
    DeviceState,
    DeviceType,
    RoomDefinition,
)


def _room(room_id: str, display_name: str, aliases: list[str]) -> RoomDefinition:
    return RoomDefinition(room_id=room_id, display_name=display_name, aliases=aliases)


def _capability(
    capability: DeviceCapabilityType,
    *,
    readable: bool = False,
    writable: bool = False,
    risk_level: RiskLevel = RiskLevel.MEDIUM,
    requires_confirmation: bool = True,
    parameters_schema: dict | None = None,
) -> DeviceCapability:
    return DeviceCapability(
        capability=capability,
        supported=True,
        readable=readable,
        writable=writable,
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        parameters_schema=parameters_schema or {},
    )


def _device(
    device_id: str,
    display_name: str,
    device_type: DeviceType,
    room_id: str,
    aliases: list[str],
    capabilities: list[DeviceCapability],
) -> DeviceDefinition:
    return DeviceDefinition(
        device_id=device_id,
        display_name=display_name,
        device_type=device_type,
        room_id=room_id,
        aliases=aliases,
        capabilities=capabilities,
        state=DeviceState(device_id=device_id),
        source=DeviceSource.BUILT_IN,
        enabled=True,
    )


class DeviceRegistry:
    def __init__(self) -> None:
        self._rooms = {
            room.room_id: room
            for room in [
                _room("salon", "Salon", ["oturma odasi"]),
                _room("calisma-odasi", "Calisma Odasi", ["ofis", "calisma odasi"]),
                _room("yatak-odasi", "Yatak Odasi", ["yatak odasi"]),
                _room("mutfak", "Mutfak", []),
                _room("koridor", "Koridor", ["hol"]),
            ]
        }
        self._devices = {
            device.device_id: device
            for device in [
                _device(
                    "salon-isigi",
                    "Salon Isigi",
                    DeviceType.LIGHT,
                    "salon",
                    ["salon lambasi", "ana isik", "ana isigi"],
                    [
                        _capability(DeviceCapabilityType.POWER, writable=True),
                        _capability(DeviceCapabilityType.BRIGHTNESS, writable=True, parameters_schema={"brightness": "0-100"}),
                        _capability(DeviceCapabilityType.STATE_QUERY, readable=True, writable=False, risk_level=RiskLevel.SAFE_READONLY, requires_confirmation=False),
                    ],
                ),
                _device(
                    "calisma-odasi-isigi",
                    "Calisma Odasi Isigi",
                    DeviceType.LIGHT,
                    "calisma-odasi",
                    ["ofis isigi"],
                    [
                        _capability(DeviceCapabilityType.POWER, writable=True),
                        _capability(DeviceCapabilityType.BRIGHTNESS, writable=True, parameters_schema={"brightness": "0-100"}),
                    ],
                ),
                _device(
                    "yatak-odasi-isigi",
                    "Yatak Odasi Isigi",
                    DeviceType.LIGHT,
                    "yatak-odasi",
                    [],
                    [
                        _capability(DeviceCapabilityType.POWER, writable=True),
                        _capability(DeviceCapabilityType.BRIGHTNESS, writable=True, parameters_schema={"brightness": "0-100"}),
                    ],
                ),
                _device(
                    "salon-klimasi",
                    "Salon Klimasi",
                    DeviceType.THERMOSTAT,
                    "salon",
                    ["klima"],
                    [
                        _capability(DeviceCapabilityType.TEMPERATURE, writable=True, parameters_schema={"temperature": "16-30"}),
                        _capability(DeviceCapabilityType.MODE, writable=True, parameters_schema={"mode": "cool|heat|auto"}),
                        _capability(DeviceCapabilityType.STATE_QUERY, readable=True, writable=False, risk_level=RiskLevel.SAFE_READONLY, requires_confirmation=False),
                    ],
                ),
                _device(
                    "bilgisayar-hoparloru",
                    "Bilgisayar Hoparloru",
                    DeviceType.SPEAKER,
                    "calisma-odasi",
                    ["masa hoparloru", "hoparlor"],
                    [
                        _capability(DeviceCapabilityType.VOLUME, writable=True, parameters_schema={"volume": "0-100"}),
                        _capability(DeviceCapabilityType.MEDIA_CONTROL, writable=True, parameters_schema={"command": "play_pause|next|previous"}),
                    ],
                ),
            ]
        }

    def list_rooms(self) -> list[RoomDefinition]:
        return list(self._rooms.values())

    def list_devices(self, room_id: str | None = None, device_type: DeviceType | None = None) -> list[DeviceDefinition]:
        devices = list(self._devices.values())
        if room_id:
            devices = [device for device in devices if device.room_id == room_id]
        if device_type:
            devices = [device for device in devices if device.device_type is device_type]
        return devices

    def get_device(self, device_id: str) -> DeviceDefinition | None:
        return self._devices.get(device_id)

    def get_room(self, room_id: str) -> RoomDefinition | None:
        return self._rooms.get(room_id)

    def find_device_by_alias(self, alias: str) -> DeviceDefinition | None:
        alias_normalized = alias.strip().lower()
        for device in self._devices.values():
            if alias_normalized == device.display_name.lower() or alias_normalized in {item.lower() for item in device.aliases}:
                return device
        return None

    def find_room_by_alias(self, alias: str) -> RoomDefinition | None:
        alias_normalized = alias.strip().lower()
        for room in self._rooms.values():
            if alias_normalized == room.display_name.lower() or alias_normalized in {item.lower() for item in room.aliases}:
                return room
        return None

    def add_device(self, definition: DeviceDefinition) -> None:
        self._devices[definition.device_id] = definition

    def add_room(self, definition: RoomDefinition) -> None:
        self._rooms[definition.room_id] = definition
