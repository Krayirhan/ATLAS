"""Demo data models for Sprint 50 end-to-end personal assistant demo."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DemoCategory(str, Enum):
    CHAT = "chat"
    VOICE = "voice"
    PC_PREVIEW = "pc_preview"
    DEVICE = "device"
    HOME_PREVIEW = "home_preview"
    ROUTINE = "routine"
    MEMORY = "memory"
    REMINDER = "reminder"
    CALENDAR = "calendar"
    PANEL = "panel"
    SAFETY = "safety"
    MIXED = "mixed"


class CommandSurface(str, Enum):
    CHAT = "chat"
    VOICE = "voice"
    INTENT = "intent"
    PC_PREVIEW = "pc_preview"
    DEVICE = "device"
    HOME_PREVIEW = "home_preview"
    ROUTINE = "routine"
    MEMORY_PERSONAL = "memory_personal"
    REMINDER = "reminder"
    CALENDAR = "calendar"
    PANEL = "panel"


class DemoScenario(BaseModel):
    scenario_id: str
    title: str
    description: str
    category: DemoCategory
    input_text: str
    command_surface: CommandSurface
    expected_response_type: str
    expected_safety_flags: dict[str, bool] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DemoStep(BaseModel):
    step_id: str
    scenario_id: str
    title: str
    command_surface: CommandSurface
    input_text: str
    result_summary: str = ""
    passed: bool = False
    warnings: list[str] = Field(default_factory=list)
    safety_flags: dict[str, bool] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DemoResult(BaseModel):
    scenario_id: str
    title: str
    passed: bool
    response_type: str
    assistant_message: str
    command_surface: CommandSurface
    safety_flags: dict[str, bool] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    raw_result_summary: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class DemoReport(BaseModel):
    report_id: str
    created_at: datetime = Field(default_factory=_utcnow)
    project_name: str
    total_scenarios: int
    passed_scenarios: int
    failed_scenarios: int
    results: list[DemoResult] = Field(default_factory=list)
    safety_summary: dict[str, Any] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
