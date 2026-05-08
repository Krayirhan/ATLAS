from app.execution.models import (
    ExecutionEligibility,
    ExecutionMode,
    ExecutionPlan,
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
    RollbackPlan,
)


def test_execution_request_builds() -> None:
    request = ExecutionRequest(request_id="req-1", source="text", requested_mode=ExecutionMode.PREVIEW_ONLY)
    assert request.request_id == "req-1"


def test_execution_eligibility_builds() -> None:
    eligibility = ExecutionEligibility(
        eligible=True,
        allowed_by_policy=True,
        allowed_by_allowlist=True,
        requires_panel_approval=True,
        has_panel_approval=False,
        risk_level="low",
        action_type="pc.open_app",
        target="Chrome",
        reason="ok",
    )
    assert eligibility.eligible is True


def test_execution_plan_builds() -> None:
    plan = ExecutionPlan(
        execution_id="exec-1",
        action_type="pc.open_app",
        target="Chrome",
        resolved_target="Chrome",
        mode=ExecutionMode.PREVIEW_ONLY,
        eligible=True,
        executable=False,
        will_execute=False,
        dry_run=True,
        requires_approval=True,
        approved=False,
        rollback_available=False,
        rollback_plan=RollbackPlan(available=False),
    )
    assert plan.execution_id == "exec-1"


def test_execution_result_builds() -> None:
    result = ExecutionResult(
        execution_id="exec-1",
        status=ExecutionStatus.PREVIEWED,
        executed=False,
        dry_run=True,
        message="Gercek islem yapilmadi.",
    )
    assert result.status is ExecutionStatus.PREVIEWED

