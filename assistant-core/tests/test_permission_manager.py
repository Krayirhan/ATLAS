from __future__ import annotations

from app.actions import (
    ActionCandidate,
    ActionSource,
    ActionStatus,
    ActionType,
    IntentCategory,
    PermissionManager,
    PermissionStatus,
    RiskLevel,
)


def _candidate(
    *,
    action_type: ActionType,
    intent_category: IntentCategory,
    risk_level: RiskLevel,
    target: str,
    source: ActionSource = ActionSource.TEXT,
    requires_confirmation: bool | None = None,
    blocked_reason: str = "",
    audit_metadata: dict | None = None,
) -> ActionCandidate:
    if requires_confirmation is None:
        requires_confirmation = risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH}
    return ActionCandidate(
        action_id=f"act-{action_type.value}",
        action_type=action_type,
        target=target,
        parameters={"target": target},
        source=source,
        user_goal=f"{target} icin {action_type.value}",
        intent_category=intent_category,
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        dry_run_supported=True,
        reversible=risk_level not in {RiskLevel.BLOCKED, RiskLevel.HIGH},
        expected_result=f"{action_type.value} preview result.",
        blocked_reason=blocked_reason,
        audit_metadata=audit_metadata or {},
    )


def test_safe_readonly_action_decision() -> None:
    decision = PermissionManager().decide(
        _candidate(
            action_type=ActionType.PC_SYSTEM_INFO,
            intent_category=IntentCategory.PC_SYSTEM_INFO,
            risk_level=RiskLevel.SAFE_READONLY,
            target="system",
        )
    )

    assert decision.status is PermissionStatus.SAFE_READONLY
    assert decision.requires_confirmation is False
    assert decision.requires_clarification is False
    assert decision.blocked is False
    assert decision.preview is not None
    assert decision.preview.will_change_state is False


def test_low_open_app_preview_allowed() -> None:
    decision = PermissionManager().decide(
        _candidate(
            action_type=ActionType.PC_OPEN_APP,
            intent_category=IntentCategory.PC_OPEN_APP,
            risk_level=RiskLevel.LOW,
            target="Chrome",
        )
    )

    assert decision.status is PermissionStatus.PREVIEW_ALLOWED
    assert decision.allowed_to_execute is True
    assert decision.requires_confirmation is False
    assert decision.preview is not None
    assert decision.preview.safe_to_execute is True


def test_medium_device_action_requires_confirmation() -> None:
    decision = PermissionManager().decide(
        _candidate(
            action_type=ActionType.DEVICE_TURN_ON,
            intent_category=IntentCategory.DEVICE_TURN_ON,
            risk_level=RiskLevel.MEDIUM,
            target="salon isigi",
        )
    )

    assert decision.status is PermissionStatus.CONFIRMATION_REQUIRED
    assert decision.allowed_to_execute is False
    assert decision.requires_confirmation is True
    assert "onayliyor musun" in decision.confirmation_prompt


def test_high_shutdown_requires_confirmation_and_warning() -> None:
    decision = PermissionManager().decide(
        _candidate(
            action_type=ActionType.PC_SHUTDOWN,
            intent_category=IntentCategory.UNKNOWN,
            risk_level=RiskLevel.HIGH,
            target="bilgisayar",
        )
    )

    assert decision.status is PermissionStatus.CLARIFICATION_REQUIRED
    assert decision.allowed_to_execute is False

    direct_high = PermissionManager().decide(
        _candidate(
            action_type=ActionType.PC_SHUTDOWN,
            intent_category=IntentCategory.CONVERSATION_STATUS,
            risk_level=RiskLevel.HIGH,
            target="bilgisayar",
        )
    )
    assert direct_high.status is PermissionStatus.CONFIRMATION_REQUIRED
    assert direct_high.requires_confirmation is True
    assert direct_high.warnings


def test_blocked_file_delete_decision() -> None:
    decision = PermissionManager().decide(
        _candidate(
            action_type=ActionType.FILE_DELETE,
            intent_category=IntentCategory.BLOCKED,
            risk_level=RiskLevel.BLOCKED,
            target="report.docx",
            requires_confirmation=False,
            blocked_reason="file.delete MVP'de engellidir.",
        )
    )

    assert decision.status is PermissionStatus.BLOCKED
    assert decision.blocked is True
    assert decision.allowed_to_execute is False
    assert decision.requires_confirmation is False
    assert decision.audit_metadata["execution_attempted"] is False


def test_ambiguous_intent_requires_clarification() -> None:
    decision = PermissionManager().decide(
        _candidate(
            action_type=ActionType.DEVICE_TURN_ON,
            intent_category=IntentCategory.AMBIGUOUS,
            risk_level=RiskLevel.MEDIUM,
            target="isik",
        )
    )

    assert decision.status is PermissionStatus.CLARIFICATION_REQUIRED
    assert decision.requires_clarification is True
    assert decision.allowed_to_execute is False
    assert decision.preview is not None
    assert decision.preview.requires_clarification is True


def test_unknown_intent_requires_clarification() -> None:
    decision = PermissionManager().decide(
        _candidate(
            action_type=ActionType.PC_OPEN_APP,
            intent_category=IntentCategory.UNKNOWN,
            risk_level=RiskLevel.LOW,
            target="Chrome",
        )
    )

    assert decision.status is PermissionStatus.CLARIFICATION_REQUIRED
    assert decision.requires_clarification is True


def test_missing_target_requires_clarification() -> None:
    decision = PermissionManager().decide(
        _candidate(
            action_type=ActionType.PC_OPEN_APP,
            intent_category=IntentCategory.PC_OPEN_APP,
            risk_level=RiskLevel.LOW,
            target="",
        )
    )

    assert decision.status is PermissionStatus.CLARIFICATION_REQUIRED
    assert decision.requires_clarification is True
    assert "Hedef" in decision.confirmation_prompt


def test_voice_medium_action_requires_confirmation() -> None:
    decision = PermissionManager().decide(
        _candidate(
            action_type=ActionType.DEVICE_TURN_ON,
            intent_category=IntentCategory.DEVICE_TURN_ON,
            risk_level=RiskLevel.MEDIUM,
            target="salon isigi",
            source=ActionSource.VOICE,
            audit_metadata={"confidence": 0.95},
        )
    )

    assert decision.status is PermissionStatus.CONFIRMATION_REQUIRED
    assert decision.requires_confirmation is True
    assert decision.confirmation_prompt.startswith("Sesli komut")


def test_voice_low_confidence_requires_clarification() -> None:
    decision = PermissionManager().decide(
        _candidate(
            action_type=ActionType.DEVICE_TURN_ON,
            intent_category=IntentCategory.DEVICE_TURN_ON,
            risk_level=RiskLevel.MEDIUM,
            target="salon isigi",
            source=ActionSource.VOICE,
            audit_metadata={"confidence": 0.41},
        )
    )

    assert decision.status is PermissionStatus.CLARIFICATION_REQUIRED
    assert decision.requires_clarification is True


def test_confirm_false_returns_denied_result() -> None:
    manager = PermissionManager()
    decision = manager.decide(
        _candidate(
            action_type=ActionType.DEVICE_TURN_ON,
            intent_category=IntentCategory.DEVICE_TURN_ON,
            risk_level=RiskLevel.MEDIUM,
            target="salon isigi",
        )
    )

    result = manager.confirm(decision, confirmed=False)

    assert result.status is ActionStatus.DENIED
    assert result.executed is False
    assert result.dry_run is True
    assert result.audit_metadata["execution_attempted"] is False


def test_cancel_returns_cancelled_result() -> None:
    manager = PermissionManager()
    decision = manager.decide(
        _candidate(
            action_type=ActionType.DEVICE_TURN_ON,
            intent_category=IntentCategory.DEVICE_TURN_ON,
            risk_level=RiskLevel.MEDIUM,
            target="salon isigi",
        )
    )

    result = manager.cancel(decision)

    assert result.status is ActionStatus.CANCELLED
    assert result.executed is False
    assert result.audit_metadata["execution_attempted"] is False


def test_confirm_true_produces_approved_result_without_execution() -> None:
    manager = PermissionManager()
    decision = manager.decide(
        _candidate(
            action_type=ActionType.DEVICE_TURN_ON,
            intent_category=IntentCategory.DEVICE_TURN_ON,
            risk_level=RiskLevel.MEDIUM,
            target="salon isigi",
        )
    )

    result = manager.confirm(decision, confirmed=True)

    assert result.status is ActionStatus.APPROVED
    assert result.executed is False
    assert result.dry_run is True
    assert result.audit_metadata["execution_attempted"] is False


def test_permission_manager_has_no_adapter_dependency() -> None:
    manager = PermissionManager()

    assert "adapter" not in manager.__dict__
    assert "executor" not in manager.__dict__
