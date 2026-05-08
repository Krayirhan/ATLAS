"""Canonical intent, action, and permission enums.

These are schema contracts only. They do not execute actions or choose adapters.
"""

from __future__ import annotations

from enum import Enum


class IntentCategory(str, Enum):
    CONVERSATION_QUESTION = "conversation.question"
    CONVERSATION_STATUS = "conversation.status"
    PERSONAL_MEMORY_QUERY = "personal.memory_query"
    PERSONAL_PREFERENCE_SET = "personal.preference_set"
    PC_OPEN_APP = "pc.open_app"
    PC_OPEN_FOLDER = "pc.open_folder"
    PC_SYSTEM_INFO = "pc.system_info"
    PC_MEDIA_CONTROL = "pc.media_control"
    PC_VOLUME_CONTROL = "pc.volume_control"
    BROWSER_SEARCH = "browser.search"
    FILE_SEARCH = "file.search"
    ROUTINE_CREATE = "routine.create"
    ROUTINE_RUN = "routine.run"
    ROUTINE_PREVIEW = "routine.preview"
    REMINDER_CREATE = "reminder.create"
    CALENDAR_QUERY = "calendar.query"
    CALENDAR_EVENT_DRAFT = "calendar.event_draft"
    DEVICE_STATE_QUERY = "device.state_query"
    DEVICE_TURN_ON = "device.turn_on"
    DEVICE_TURN_OFF = "device.turn_off"
    DEVICE_SET_BRIGHTNESS = "device.set_brightness"
    DEVICE_SET_TEMPERATURE = "device.set_temperature"
    UNKNOWN = "unknown"
    AMBIGUOUS = "ambiguous"
    BLOCKED = "blocked"


class ActionType(str, Enum):
    PC_SYSTEM_INFO = "pc.system_info"
    FILE_SEARCH = "file.search"
    DEVICE_STATE_QUERY = "device.state_query"
    CALENDAR_QUERY = "calendar.query"
    CALENDAR_EVENT_DRAFT = "calendar.event_draft"
    ROUTINE_PREVIEW = "routine.preview"
    REMINDER_PREVIEW = "reminder.preview"
    PC_OPEN_APP = "pc.open_app"
    PC_OPEN_FOLDER = "pc.open_folder"
    BROWSER_SEARCH = "browser.search"
    PC_MEDIA_PLAY_PAUSE = "pc.media.play_pause"
    PC_MEDIA_NEXT = "pc.media.next"
    PC_MEDIA_PREVIOUS = "pc.media.previous"
    PC_VOLUME_SET = "pc.volume.set"
    PC_VOLUME_MUTE_TOGGLE = "pc.volume.mute_toggle"
    REMINDER_CREATE = "reminder.create"
    ROUTINE_CREATE = "routine.create"
    ROUTINE_RUN = "routine.run"
    DEVICE_TURN_ON = "device.turn_on"
    DEVICE_TURN_OFF = "device.turn_off"
    DEVICE_SET_BRIGHTNESS = "device.set_brightness"
    DEVICE_SET_TEMPERATURE = "device.set_temperature"
    PC_SLEEP = "pc.sleep"
    PC_LOCK = "pc.lock"
    PC_SHUTDOWN = "pc.shutdown"
    DEVICE_UNLOCK = "device.unlock"
    DEVICE_OPEN_DOOR = "device.open_door"
    DEVICE_DISABLE_SECURITY = "device.disable_security"
    ROUTINE_RUN_HIGH_IMPACT = "routine.run_high_impact"
    FILE_DELETE = "file.delete"
    FILE_OVERWRITE = "file.overwrite"
    APP_INSTALL = "app.install"
    APP_UNINSTALL = "app.uninstall"
    REGISTRY_EDIT = "registry.edit"
    SHELL_EXECUTE_UNRESTRICTED = "shell.execute_unrestricted"
    CREDENTIAL_READ = "credential.read"
    SECRET_READ = "secret.read"
    FULL_DISK_SCAN = "full_disk_scan"
    DESTRUCTIVE_SYSTEM_CHANGE = "destructive_system_change"


class ActionSource(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    ROUTINE = "routine"
    SCHEDULE = "schedule"
    MAIN_AGENT = "main_agent"
    MANUAL = "manual"
    UNKNOWN = "unknown"


class ActionStatus(str, Enum):
    PLANNED = "planned"
    PREVIEWED = "previewed"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    APPROVED = "approved"
    DENIED = "denied"
    BLOCKED = "blocked"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class PermissionStatus(str, Enum):
    SAFE_READONLY = "safe_readonly"
    PREVIEW_ALLOWED = "preview_allowed"
    CONFIRMATION_REQUIRED = "confirmation_required"
    CLARIFICATION_REQUIRED = "clarification_required"
    DENIED = "denied"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"
