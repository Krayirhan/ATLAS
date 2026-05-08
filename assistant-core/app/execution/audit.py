from __future__ import annotations

from datetime import datetime, timezone

from app.execution.policy import EXECUTION_ENABLED_DEFAULT


def build_audit_metadata(
    *,
    execution_id: str,
    action_type: str,
    target: str,
    source: str,
    risk_level: str,
    permission_status: str,
    panel_status: str,
    allowlist_decision: str,
    requested_mode: str,
) -> dict[str, object]:
    return {
        "execution_id": execution_id,
        "action_type": action_type,
        "target": target,
        "source": source,
        "risk_level": risk_level,
        "permission_status": permission_status,
        "panel_status": panel_status,
        "allowlist_decision": allowlist_decision,
        "execution_enabled": EXECUTION_ENABLED_DEFAULT,
        "requested_mode": requested_mode,
        "real_execution_attempted": False,
        "execution_attempted": False,
        "shell_used": False,
        "network_used": False,
        "physical_device_touched": False,
        "credential_accessed": False,
        "unrestricted_shell_available": False,
        "execution_gate_enabled": False,
        "allowlist_required": True,
        "panel_approval_required": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

