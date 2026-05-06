from app.actions.risk import RiskLevel
from app.control.models import PCActionCapability

_CAPABILITIES: dict[str, PCActionCapability] = {
    # Read-only
    "pc.system_info": PCActionCapability(
        action_type="pc.system_info",
        supported=True,
        execution_supported=True,
        dry_run_supported=True,
        requires_allowlist=False,
        risk_level=RiskLevel.LOW,
        description="Retrieve basic system information.",
        limitations=["Read-only", "Does not return sensitive info"]
    ),
    
    # Preview/dry-run
    "pc.open_app": PCActionCapability(
        action_type="pc.open_app",
        supported=True,
        execution_supported=False,
        dry_run_supported=True,
        requires_allowlist=True,
        risk_level=RiskLevel.LOW,
        description="Open a system application.",
        limitations=["Preview only", "Execution not supported in MVP"]
    ),
    "pc.open_folder": PCActionCapability(
        action_type="pc.open_folder",
        supported=True,
        execution_supported=False,
        dry_run_supported=True,
        requires_allowlist=True,
        risk_level=RiskLevel.LOW,
        description="Open a system folder.",
        limitations=["Preview only", "Execution not supported in MVP"]
    ),
    "browser.search": PCActionCapability(
        action_type="browser.search",
        supported=True,
        execution_supported=False,
        dry_run_supported=True,
        requires_allowlist=True,
        risk_level=RiskLevel.LOW,
        description="Search the web using default browser.",
        limitations=["Preview only", "Execution not supported in MVP"]
    ),
    "file.search": PCActionCapability(
        action_type="file.search",
        supported=True,
        execution_supported=False,
        dry_run_supported=True,
        requires_allowlist=False,
        risk_level=RiskLevel.LOW,
        description="Search for files in safe directories.",
        limitations=["Preview only", "Execution not supported in MVP"]
    ),
    "pc.media.play_pause": PCActionCapability(
        action_type="pc.media.play_pause",
        supported=True,
        execution_supported=False,
        dry_run_supported=True,
        requires_allowlist=False,
        risk_level=RiskLevel.LOW,
        description="Play or pause current media.",
        limitations=["Preview only", "Execution not supported in MVP"]
    ),
    "pc.media.next": PCActionCapability(
        action_type="pc.media.next",
        supported=True,
        execution_supported=False,
        dry_run_supported=True,
        requires_allowlist=False,
        risk_level=RiskLevel.LOW,
        description="Skip to next media track.",
        limitations=["Preview only", "Execution not supported in MVP"]
    ),
    "pc.media.previous": PCActionCapability(
        action_type="pc.media.previous",
        supported=True,
        execution_supported=False,
        dry_run_supported=True,
        requires_allowlist=False,
        risk_level=RiskLevel.LOW,
        description="Skip to previous media track.",
        limitations=["Preview only", "Execution not supported in MVP"]
    ),
    "pc.volume.set": PCActionCapability(
        action_type="pc.volume.set",
        supported=True,
        execution_supported=False,
        dry_run_supported=True,
        requires_allowlist=False,
        risk_level=RiskLevel.LOW,
        description="Set system volume.",
        limitations=["Preview only", "Execution not supported in MVP"]
    ),
    "pc.volume.mute_toggle": PCActionCapability(
        action_type="pc.volume.mute_toggle",
        supported=True,
        execution_supported=False,
        dry_run_supported=True,
        requires_allowlist=False,
        risk_level=RiskLevel.LOW,
        description="Toggle system volume mute state.",
        limitations=["Preview only", "Execution not supported in MVP"]
    ),
}

_BLOCKED_ACTIONS = {
    "file.delete", "file.overwrite", "app.install", "app.uninstall", 
    "registry.edit", "shell.execute_unrestricted", "credential.read", 
    "secret.read", "full_disk_scan", "destructive_system_change"
}

def get_capability(action_type: str) -> PCActionCapability:
    if action_type in _BLOCKED_ACTIONS:
        return PCActionCapability(
            action_type=action_type,
            supported=False,
            execution_supported=False,
            dry_run_supported=False,
            requires_allowlist=False,
            risk_level=RiskLevel.BLOCKED,
            description="Blocked action",
            limitations=["This action is permanently blocked by safety policy."]
        )
    return _CAPABILITIES.get(action_type, PCActionCapability(
        action_type=action_type,
        supported=False,
        execution_supported=False,
        dry_run_supported=False,
        requires_allowlist=False,
        risk_level=RiskLevel.BLOCKED,
        description="Unsupported action",
        limitations=["This action is not supported by the current adapter MVP."]
    ))
