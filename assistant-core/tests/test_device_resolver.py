from __future__ import annotations

from app.devices import DeviceActionPlanner, DeviceRegistryStatus, DeviceTargetResolver


def test_resolver_salon_light_resolved() -> None:
    resolution = DeviceTargetResolver().resolve_text("Salon isigini ac")
    assert resolution.resolved is True
    assert resolution.device is not None
    assert resolution.device.device_id == "salon-isigi"


def test_resolver_bedroom_light_resolved() -> None:
    resolution = DeviceTargetResolver().resolve_text("Yatak odasi isigini kapat")
    assert resolution.resolved is True
    assert resolution.device is not None
    assert resolution.device.device_id == "yatak-odasi-isigi"


def test_resolver_alias_ana_isik_resolved() -> None:
    resolution = DeviceTargetResolver().resolve_text("Ana isigi ac")
    assert resolution.resolved is True
    assert resolution.device is not None
    assert resolution.device.device_id == "salon-isigi"


def test_resolver_isigi_ac_is_ambiguous() -> None:
    resolution = DeviceTargetResolver().resolve_text("Isigi ac")
    assert resolution.resolved is False
    assert resolution.requires_clarification is True
    assert len(resolution.candidates) >= 3


def test_resolver_klima_temperature_resolved() -> None:
    resolution = DeviceTargetResolver().resolve_text("Klimayi 24 derece yap")
    assert resolution.resolved is True
    assert resolution.device is not None
    assert resolution.device.device_type.value == "thermostat"


def test_resolver_kamera_is_blocked() -> None:
    resolution = DeviceTargetResolver().resolve_text("Kamerayi ac")
    assert resolution.resolved is False
    assert resolution.metadata["blocked"] is True


def test_planner_ambiguous_text_returns_ambiguous_status() -> None:
    result = DeviceActionPlanner().preview_device_action("Isigi ac")
    assert result.status is DeviceRegistryStatus.AMBIGUOUS
    assert result.resolution is not None
    assert result.resolution.requires_clarification is True
