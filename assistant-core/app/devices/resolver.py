from __future__ import annotations

import re

from app.actions.models import ActionCandidate
from app.devices.models import DeviceDefinition, DeviceTargetResolution, DeviceType, RoomDefinition
from app.devices.policy import should_block_text, text_block_reason
from app.devices.registry import DeviceRegistry
from app.personal_memory.models import MemoryType
from app.personal_memory.store import get_store


def _normalize(text: str) -> str:
    normalized = text.strip().lower()
    normalized = normalized.translate(str.maketrans({"ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u"}))
    normalized = re.sub(r"['\"]", "", normalized)
    normalized = re.sub(r"[!?.,:()]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


class DeviceTargetResolver:
    def __init__(self, registry: DeviceRegistry | None = None) -> None:
        self.registry = registry or DeviceRegistry()

    def resolve_text(self, text: str) -> DeviceTargetResolution:
        normalized = _normalize(text)
        if should_block_text(normalized):
            return DeviceTargetResolution(
                raw_text=text,
                resolved=False,
                ambiguity_reason=text_block_reason(normalized),
                requires_clarification=False,
                confidence=0.98,
                warnings=[text_block_reason(normalized)],
                metadata={"blocked": True},
            )

        memory_device = self._find_device_alias_from_memory(normalized)
        if memory_device is not None:
            room = self.registry.get_room(memory_device.room_id)
            return DeviceTargetResolution(
                raw_text=text,
                resolved=True,
                device=memory_device,
                room=room,
                confidence=0.9,
                metadata={"resolution_source": "memory_alias"},
            )

        for candidate in self.registry.list_devices():
            aliases = [_normalize(candidate.display_name), *[_normalize(alias) for alias in candidate.aliases]]
            if any(alias and alias in normalized for alias in aliases):
                room = self.registry.get_room(candidate.room_id)
                return DeviceTargetResolution(
                    raw_text=text,
                    resolved=True,
                    device=candidate,
                    room=room,
                    confidence=0.95,
                    metadata={"resolution_source": "device_alias"},
                )

        room_name = self._extract_room_name(normalized)
        device_type = self._extract_device_type(normalized)
        if room_name and device_type:
            return self.resolve_room_device(room_name, device_type.value)

        if device_type is DeviceType.LIGHT:
            candidates = self.registry.list_devices(device_type=DeviceType.LIGHT)
            return DeviceTargetResolution(
                raw_text=text,
                resolved=False,
                candidates=candidates,
                ambiguity_reason="Hangi isigin kastedildigi net degil.",
                requires_clarification=True,
                confidence=0.35,
                warnings=["Ambiguous light target."],
                metadata={"resolution_source": "device_type_only"},
            )

        if device_type is DeviceType.THERMOSTAT:
            candidates = self.registry.list_devices(device_type=DeviceType.THERMOSTAT)
            if len(candidates) == 1:
                device = candidates[0]
                room = self.registry.get_room(device.room_id)
                return DeviceTargetResolution(
                    raw_text=text,
                    resolved=True,
                    device=device,
                    room=room,
                    confidence=0.82,
                    metadata={"resolution_source": "single_thermostat_default"},
                )

        return DeviceTargetResolution(
            raw_text=text,
            resolved=False,
            ambiguity_reason="Cihaz veya oda hedefi cozulmedi.",
            requires_clarification=True,
            confidence=0.2,
            warnings=["No device target match."],
            metadata={"resolution_source": "none"},
        )

    def resolve_action(self, action: ActionCandidate) -> DeviceTargetResolution:
        if action.target.strip():
            resolution = self.resolve_text(action.target)
            if resolution.resolved or resolution.requires_clarification or resolution.metadata.get("blocked"):
                return resolution
        raw_text = action.user_goal or action.target
        return self.resolve_text(raw_text)

    def resolve_room_device(self, room_name: str, device_type: str) -> DeviceTargetResolution:
        room = self.registry.find_room_by_alias(_normalize(room_name))
        if room is None:
            return DeviceTargetResolution(
                raw_text=f"{room_name} {device_type}",
                resolved=False,
                ambiguity_reason="Oda bulunamadi.",
                requires_clarification=True,
                confidence=0.2,
            )
        dtype = DeviceType(device_type) if device_type in {item.value for item in DeviceType} else DeviceType.UNKNOWN
        devices = self.registry.list_devices(room_id=room.room_id, device_type=dtype)
        if len(devices) == 1:
            return DeviceTargetResolution(
                raw_text=f"{room_name} {device_type}",
                resolved=True,
                device=devices[0],
                room=room,
                confidence=0.96,
                metadata={"resolution_source": "room_device"},
            )
        if len(devices) > 1:
            return DeviceTargetResolution(
                raw_text=f"{room_name} {device_type}",
                resolved=False,
                room=room,
                candidates=devices,
                ambiguity_reason="Odada birden fazla uygun cihaz var.",
                requires_clarification=True,
                confidence=0.45,
            )
        return DeviceTargetResolution(
            raw_text=f"{room_name} {device_type}",
            resolved=False,
            room=room,
            ambiguity_reason="Bu odada uygun cihaz bulunamadi.",
            requires_clarification=True,
            confidence=0.2,
        )

    def list_candidates(self, text: str) -> list[DeviceDefinition]:
        normalized = _normalize(text)
        device_type = self._extract_device_type(normalized)
        if device_type is not None and device_type is not DeviceType.UNKNOWN:
            return self.registry.list_devices(device_type=device_type)
        return self.registry.list_devices()

    def _extract_room_name(self, normalized_text: str) -> str:
        room_aliases = {alias.lower(): room.display_name for room in self.registry.list_rooms() for alias in [room.display_name, *room.aliases]}
        room_aliases.update(self._memory_room_aliases())
        for alias, display_name in room_aliases.items():
            if alias in normalized_text:
                return display_name
        return ""

    def _extract_device_type(self, normalized_text: str) -> DeviceType | None:
        if "isik" in normalized_text or "isig" in normalized_text or "lamba" in normalized_text:
            return DeviceType.LIGHT
        if "klima" in normalized_text or "termostat" in normalized_text:
            return DeviceType.THERMOSTAT
        if "hoparlor" in normalized_text:
            return DeviceType.SPEAKER
        if "kamera" in normalized_text:
            return DeviceType.CAMERA
        if "kapi" in normalized_text:
            return DeviceType.LOCK
        return None

    def _find_device_alias_from_memory(self, normalized_text: str) -> DeviceDefinition | None:
        for item in get_store().list_all(MemoryType.DEVICE_ALIAS):
            alias = _normalize(str(item.key))
            if alias and alias in normalized_text:
                value_text = _normalize(str(item.value))
                device = self.registry.find_device_by_alias(value_text)
                if device is not None:
                    return device
        return None

    def _memory_room_aliases(self) -> dict[str, str]:
        aliases: dict[str, str] = {}
        for item in get_store().list_all(MemoryType.ROOM_ALIAS):
            aliases[_normalize(str(item.key))] = str(item.value)
        return aliases
