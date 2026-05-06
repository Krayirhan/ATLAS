from app.control.pc_adapter import PCControlAdapter
from app.actions.models import ActionCandidate, PermissionDecision
from app.actions.types import ActionSource, PermissionStatus
from app.actions.risk import RiskLevel

def test_adapter_system_info():
    adapter = PCControlAdapter()
    assert adapter.supports("pc.system_info")
    
    action = ActionCandidate(
        action_id="1",
        action_type="pc.system_info",
        target="",
        parameters={},
        source=ActionSource.TEXT,
        user_goal="Get sys info",
        intent_category="pc.system_info",
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        dry_run_supported=True,
        reversible=True,
        expected_result="sys info"
    )
    decision = PermissionDecision(
        action_id="1",
        status=PermissionStatus.PREVIEW_ALLOWED,
        risk_level=RiskLevel.LOW,
        allowed_to_execute=True,
        requires_confirmation=False,
        requires_clarification=False,
        blocked=False,
        reason="ok",
        confirmation_prompt="",
        warnings=[],
        audit_metadata={},
        next_step="execute"
    )
    
    # Test plan
    plan = adapter.build_plan(action, decision, dry_run=False)
    assert plan.action_type == "pc.system_info"
    assert plan.execution_allowed
    assert plan.executable
    
    # Test execute
    result = adapter.execute(plan)
    assert result.executed
    assert "os" in result.data

def test_adapter_open_app_dry_run():
    adapter = PCControlAdapter()
    
    action = ActionCandidate(
        action_id="2",
        action_type="pc.open_app",
        target="Chrome",
        parameters={},
        source=ActionSource.TEXT,
        user_goal="Open Chrome",
        intent_category="pc.open_app",
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        dry_run_supported=True,
        reversible=True,
        expected_result="Chrome opens"
    )
    decision = PermissionDecision(
        action_id="2",
        status=PermissionStatus.PREVIEW_ALLOWED,
        risk_level=RiskLevel.LOW,
        allowed_to_execute=True,
        requires_confirmation=False,
        requires_clarification=False,
        blocked=False,
        reason="ok",
        confirmation_prompt="",
        warnings=[],
        audit_metadata={},
        next_step="execute"
    )
    
    plan = adapter.build_plan(action, decision, dry_run=True)
    assert plan.execution_allowed is False # execution not supported in MVP
    
    result = adapter.execute(plan)
    assert result.executed is False
    assert result.dry_run is True

def test_adapter_blocked_action():
    adapter = PCControlAdapter()
    
    action = ActionCandidate(
        action_id="3",
        action_type="file.delete",
        target="some_file",
        parameters={},
        source=ActionSource.TEXT,
        user_goal="delete file",
        intent_category="unknown",
        risk_level=RiskLevel.BLOCKED,
        requires_confirmation=False,
        dry_run_supported=False,
        reversible=False,
        expected_result="",
        blocked_reason="blocked"
    )
    decision = PermissionDecision(
        action_id="3",
        status=PermissionStatus.BLOCKED,
        risk_level=RiskLevel.BLOCKED,
        allowed_to_execute=False,
        requires_confirmation=False,
        requires_clarification=False,
        blocked=True,
        reason="blocked action",
        confirmation_prompt="",
        warnings=[],
        audit_metadata={},
        next_step="block"
    )
    
    plan = adapter.build_plan(action, decision)
    assert plan.execution_allowed is False
    assert plan.executable is False
    
    result = adapter.execute(plan)
    assert result.executed is False
