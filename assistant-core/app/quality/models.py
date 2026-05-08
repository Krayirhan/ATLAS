from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


SAFETY_INVARIANT_FALSE_FLAGS: tuple[str, ...] = (
    "execution_attempted",
    "real_execution_attempted",
    "physical_device_touched",
    "network_used",
    "microphone_used",
    "wake_word_used",
    "audio_retained",
    "external_calendar_used",
    "os_notification_sent",
    "credential_accessed",
    "shell_used",
    "unrestricted_shell_available",
    "execution_gate_enabled",
)

SAFETY_INVARIANT_TRUE_FLAGS: tuple[str, ...] = (
    "allowlist_required",
    "panel_approval_required",
)

SAFETY_INVARIANT_FLAGS: tuple[str, ...] = SAFETY_INVARIANT_FALSE_FLAGS + SAFETY_INVARIANT_TRUE_FLAGS

SAFETY_INVARIANT_EXPECTED: dict[str, bool] = {
    **{flag: False for flag in SAFETY_INVARIANT_FALSE_FLAGS},
    **{flag: True for flag in SAFETY_INVARIANT_TRUE_FLAGS},
}


class SafetyInvariantCheck(BaseModel):
    name: str
    command_surface: str
    passed: bool
    flags: dict[str, bool] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SafetyInvariantReport(BaseModel):
    created_at: datetime = Field(default_factory=_utcnow)
    total_checks: int
    passed: int
    failed: int
    checks: list[SafetyInvariantCheck] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class LatencyMeasurement(BaseModel):
    name: str
    command_surface: str
    duration_ms: int
    threshold_ms: int
    passed: bool
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LatencyReport(BaseModel):
    created_at: datetime = Field(default_factory=_utcnow)
    total_measurements: int
    passed: int
    failed: int
    measurements: list[LatencyMeasurement] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class HardeningReport(BaseModel):
    created_at: datetime = Field(default_factory=_utcnow)
    project_name: str
    modes: list[str] = Field(default_factory=list)
    safety_report: SafetyInvariantReport | None = None
    latency_report: LatencyReport | None = None
    recommendations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
