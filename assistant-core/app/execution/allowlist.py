from __future__ import annotations

from typing import Any


ALLOWED_ACTION_TYPES: tuple[str, ...] = (
    "pc.open_app",
    "pc.open_folder",
    "pc.system_info",
    "browser.search",
    "pc.media.play_pause",
    "pc.media.next",
    "pc.media.previous",
    "pc.volume.set",
    "pc.volume.mute_toggle",
)

BLOCKED_ACTION_TYPES: tuple[str, ...] = (
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
    "device.turn_on",
    "device.turn_off",
    "home.write_state",
    "mqtt.publish",
    "home_assistant.call_service",
)

_CANONICAL_TARGETS = {
    "chrome": "Chrome",
    "notepad": "Notepad",
    "not defteri": "Notepad",
    "calculator": "Calculator",
    "hesap makinesi": "Calculator",
    "vs code": "VS Code",
    "visual studio code": "VS Code",
}

_TARGET_RESTRICTED_ACTIONS = {"pc.open_app"}

_POLICIES: dict[str, dict[str, Any]] = {
    "pc.open_app": {
        "allowed": True,
        "risk_level": "low",
        "requires_panel_approval": True,
        "targets": ["Chrome", "Notepad", "Calculator", "VS Code"],
        "notes": ["Low-risk PC app open candidate.", "Real execution remains disabled in Sprint 52."],
    },
    "pc.open_folder": {
        "allowed": True,
        "risk_level": "low",
        "requires_panel_approval": True,
        "targets": [],
        "notes": ["Folder open planning only.", "Real execution remains disabled in Sprint 52."],
    },
    "pc.system_info": {
        "allowed": True,
        "risk_level": "safe_readonly",
        "requires_panel_approval": True,
        "targets": [],
        "notes": ["Read-only system information planning only."],
    },
    "browser.search": {
        "allowed": True,
        "risk_level": "low",
        "requires_panel_approval": True,
        "targets": [],
        "notes": ["Browser search planning only."],
    },
    "pc.media.play_pause": {
        "allowed": True,
        "risk_level": "low",
        "requires_panel_approval": True,
        "targets": [],
        "notes": ["Media control planning only."],
    },
    "pc.media.next": {
        "allowed": True,
        "risk_level": "low",
        "requires_panel_approval": True,
        "targets": [],
        "notes": ["Media control planning only."],
    },
    "pc.media.previous": {
        "allowed": True,
        "risk_level": "low",
        "requires_panel_approval": True,
        "targets": [],
        "notes": ["Media control planning only."],
    },
    "pc.volume.set": {
        "allowed": True,
        "risk_level": "low",
        "requires_panel_approval": True,
        "targets": [],
        "notes": ["Volume control planning only."],
    },
    "pc.volume.mute_toggle": {
        "allowed": True,
        "risk_level": "low",
        "requires_panel_approval": True,
        "targets": [],
        "notes": ["Volume control planning only."],
    },
}


def normalize_target(target: str) -> str:
    return _CANONICAL_TARGETS.get(target.strip().lower(), target.strip())


class ExecutionAllowlist:
    def is_action_allowed(self, action_type: str) -> bool:
        return action_type in ALLOWED_ACTION_TYPES

    def is_target_allowed(self, action_type: str, target: str) -> bool:
        if action_type in BLOCKED_ACTION_TYPES:
            return False
        if action_type not in _TARGET_RESTRICTED_ACTIONS:
            return True
        normalized = normalize_target(target)
        return normalized in _POLICIES[action_type]["targets"]

    def get_policy(self, action_type: str) -> dict[str, Any]:
        if action_type in BLOCKED_ACTION_TYPES:
            return {
                "action_type": action_type,
                "allowed": False,
                "blocked": True,
                "risk_level": "blocked",
                "requires_panel_approval": True,
                "targets": [],
                "notes": ["Explicitly blocked by Sprint 52 execution policy."],
            }
        policy = _POLICIES.get(action_type)
        if policy is None:
            return {
                "action_type": action_type,
                "allowed": False,
                "blocked": True,
                "risk_level": "blocked",
                "requires_panel_approval": True,
                "targets": [],
                "notes": ["Unknown or unsupported action type."],
            }
        return {"action_type": action_type, **policy}

    def explain(self, action_type: str) -> str:
        policy = self.get_policy(action_type)
        if policy["allowed"]:
            return f"{action_type} allowlist icinde, ancak Sprint 52 boyunca gercek execution kapali."
        return f"{action_type} allowlist disinda veya explicit blocked."

