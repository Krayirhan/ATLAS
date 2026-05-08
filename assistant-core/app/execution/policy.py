from __future__ import annotations

from app.execution.models import ExecutionMode


EXECUTION_ENABLED_DEFAULT = False
DEFAULT_EXECUTION_MODE = ExecutionMode.PREVIEW_ONLY

NON_EXECUTABLE_MODES: tuple[ExecutionMode, ...] = (
    ExecutionMode.DISABLED,
    ExecutionMode.DRY_RUN,
    ExecutionMode.PREVIEW_ONLY,
)

NEGATIVE_INVARIANT_FLAGS: tuple[str, ...] = (
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

POSITIVE_INVARIANT_FLAGS: tuple[str, ...] = (
    "allowlist_required",
    "panel_approval_required",
)

BLOCKED_PERMISSION_STATUSES = {"blocked", "clarification_required", "denied", "cancelled"}
BLOCKED_PANEL_STATUSES = {"blocked", "denied", "cancelled"}
EXPIRED_PANEL_STATUSES = {"expired"}
APPROVED_PANEL_STATUSES = {"approved"}
APPROVED_PANEL_TYPES = {"approved_preview"}

HOME_ACTION_PREFIXES = ("device.", "home.")
HOME_ACTION_TYPES = {"mqtt.publish", "home_assistant.call_service", "home.write_state"}
NON_PC_EXECUTION_ACTION_TYPES = {
    "reminder.create",
    "calendar.event_draft",
    "calendar.query",
    "notification.send",
    "notification.preview",
    "routine.create",
    "routine.run",
    "routine.run_high_impact",
}

BLOCKED_ACTION_TYPES = {
    "shell.execute",
    "shell.execute_unrestricted",
    "powershell.run",
    "cmd.run",
    "file.delete",
    "file.overwrite",
    "file.move",
    "registry.edit",
    "app.install",
    "app.uninstall",
    "credential.read",
    "secret.read",
    "full_disk_scan",
    "admin.operation",
}


def mode_from_text(value: str | None) -> ExecutionMode:
    if not value:
        return DEFAULT_EXECUTION_MODE
    return ExecutionMode(value)


def is_home_or_device_action(action_type: str) -> bool:
    return action_type.startswith(HOME_ACTION_PREFIXES) or action_type in HOME_ACTION_TYPES

