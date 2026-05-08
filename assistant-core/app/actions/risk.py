"""Risk-level contract for ATLAS action candidates.

This module contains classification constants only. It does not execute actions.
"""

from __future__ import annotations

from enum import Enum

from app.actions.types import ActionSource, ActionType


class RiskLevel(str, Enum):
    SAFE_READONLY = "safe_readonly"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKED = "blocked"


DEFAULT_ACTION_RISK: dict[ActionType, RiskLevel] = {
    ActionType.PC_SYSTEM_INFO: RiskLevel.SAFE_READONLY,
    ActionType.FILE_SEARCH: RiskLevel.SAFE_READONLY,
    ActionType.DEVICE_STATE_QUERY: RiskLevel.SAFE_READONLY,
    ActionType.CALENDAR_QUERY: RiskLevel.SAFE_READONLY,
    ActionType.ROUTINE_PREVIEW: RiskLevel.SAFE_READONLY,
    ActionType.REMINDER_PREVIEW: RiskLevel.SAFE_READONLY,
    ActionType.PC_OPEN_APP: RiskLevel.LOW,
    ActionType.PC_OPEN_FOLDER: RiskLevel.LOW,
    ActionType.BROWSER_SEARCH: RiskLevel.LOW,
    ActionType.PC_MEDIA_PLAY_PAUSE: RiskLevel.LOW,
    ActionType.PC_MEDIA_NEXT: RiskLevel.LOW,
    ActionType.PC_MEDIA_PREVIOUS: RiskLevel.LOW,
    ActionType.PC_VOLUME_SET: RiskLevel.LOW,
    ActionType.PC_VOLUME_MUTE_TOGGLE: RiskLevel.LOW,
    ActionType.REMINDER_CREATE: RiskLevel.MEDIUM,
    ActionType.CALENDAR_EVENT_DRAFT: RiskLevel.MEDIUM,
    ActionType.ROUTINE_CREATE: RiskLevel.MEDIUM,
    ActionType.ROUTINE_RUN: RiskLevel.MEDIUM,
    ActionType.DEVICE_TURN_ON: RiskLevel.MEDIUM,
    ActionType.DEVICE_TURN_OFF: RiskLevel.MEDIUM,
    ActionType.DEVICE_SET_BRIGHTNESS: RiskLevel.MEDIUM,
    ActionType.DEVICE_SET_TEMPERATURE: RiskLevel.MEDIUM,
    ActionType.PC_SLEEP: RiskLevel.HIGH,
    ActionType.PC_LOCK: RiskLevel.HIGH,
    ActionType.PC_SHUTDOWN: RiskLevel.HIGH,
    ActionType.DEVICE_UNLOCK: RiskLevel.HIGH,
    ActionType.DEVICE_OPEN_DOOR: RiskLevel.HIGH,
    ActionType.DEVICE_DISABLE_SECURITY: RiskLevel.HIGH,
    ActionType.ROUTINE_RUN_HIGH_IMPACT: RiskLevel.HIGH,
    ActionType.FILE_DELETE: RiskLevel.BLOCKED,
    ActionType.FILE_OVERWRITE: RiskLevel.BLOCKED,
    ActionType.APP_INSTALL: RiskLevel.BLOCKED,
    ActionType.APP_UNINSTALL: RiskLevel.BLOCKED,
    ActionType.REGISTRY_EDIT: RiskLevel.BLOCKED,
    ActionType.SHELL_EXECUTE_UNRESTRICTED: RiskLevel.BLOCKED,
    ActionType.CREDENTIAL_READ: RiskLevel.BLOCKED,
    ActionType.SECRET_READ: RiskLevel.BLOCKED,
    ActionType.FULL_DISK_SCAN: RiskLevel.BLOCKED,
    ActionType.DESTRUCTIVE_SYSTEM_CHANGE: RiskLevel.BLOCKED,
}


def requires_confirmation(risk_level: RiskLevel, *, source: ActionSource = ActionSource.UNKNOWN) -> bool:
    """Return whether the schema requires explicit confirmation.

    Voice-originated medium/high actions are intentionally included here. Low
    voice actions may still be previewed by UX policy, but are not forced by the
    Sprint 37 schema contract.
    """

    if risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH}:
        return True
    if risk_level is RiskLevel.BLOCKED:
        return False
    return False
