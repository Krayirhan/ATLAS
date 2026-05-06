from __future__ import annotations

import pytest

from app.actions.models import ActionCandidate, ActionPreview, ActionResult, ClarificationRequest, IntentResult
from app.actions.risk import RiskLevel, requires_confirmation
from app.actions.types import ActionSource, ActionStatus, ActionType, IntentCategory


def test_intent_result_can_be_created() -> None:
    result = IntentResult(
        intent_id="intent-1",
        category=IntentCategory.PC_OPEN_APP,
        confidence=0.94,
        language="tr",
        raw_text="Chrome'u ac",
        normalized_text="chrome'u ac",
        entities={"app": "Chrome"},
        target="Chrome",
        action_candidate=ActionType.PC_OPEN_APP,
    )
    assert result.category == IntentCategory.PC_OPEN_APP
    assert result.action_candidate == ActionType.PC_OPEN_APP


def test_confidence_must_be_between_zero_and_one() -> None:
    with pytest.raises(ValueError, match="confidence"):
        IntentResult(
            intent_id="intent-bad",
            category=IntentCategory.UNKNOWN,
            confidence=1.2,
            language="tr",
            raw_text="?",
            normalized_text="?",
        )


def test_action_candidate_can_be_created() -> None:
    action = ActionCandidate(
        action_id="act-1",
        action_type=ActionType.PC_OPEN_APP,
        target="Chrome",
        parameters={"app": "Chrome"},
        source=ActionSource.TEXT,
        user_goal="Chrome'u ac",
        intent_category=IntentCategory.PC_OPEN_APP,
        risk_level=RiskLevel.LOW,
        requires_confirmation=False,
        dry_run_supported=True,
        reversible=True,
        expected_result="Chrome acilir.",
    )
    assert action.action_type == ActionType.PC_OPEN_APP
    assert action.risk_level == RiskLevel.LOW


def test_risk_level_enum_values() -> None:
    assert RiskLevel.SAFE_READONLY.value == "safe_readonly"
    assert RiskLevel.BLOCKED.value == "blocked"
    assert requires_confirmation(RiskLevel.MEDIUM) is True
    assert requires_confirmation(RiskLevel.HIGH) is True
    assert requires_confirmation(RiskLevel.BLOCKED) is False


def test_blocked_action_confirmation_is_disabled() -> None:
    action = ActionCandidate(
        action_id="act-blocked",
        action_type=ActionType.FILE_DELETE,
        target="report.docx",
        parameters={"path": "report.docx"},
        source=ActionSource.TEXT,
        user_goal="Dosyayi sil",
        intent_category=IntentCategory.BLOCKED,
        risk_level=RiskLevel.LOW,
        requires_confirmation=True,
        dry_run_supported=True,
        reversible=False,
        expected_result="Dosya silinir.",
        blocked_reason="file.delete is blocked in MVP.",
    )
    assert action.risk_level == RiskLevel.BLOCKED
    assert action.requires_confirmation is False


def test_blocked_action_requires_blocked_reason() -> None:
    with pytest.raises(ValueError, match="blocked_reason"):
        ActionCandidate(
            action_id="act-blocked-no-reason",
            action_type=ActionType.SECRET_READ,
            target=".env",
            parameters={"path": ".env"},
            source=ActionSource.TEXT,
            user_goal=".env oku",
            intent_category=IntentCategory.BLOCKED,
            risk_level=RiskLevel.BLOCKED,
            requires_confirmation=False,
            dry_run_supported=True,
            reversible=False,
            expected_result="Secret okunur.",
        )


@pytest.mark.parametrize(
    ("action_type", "intent_category", "risk_level"),
    [
        (ActionType.REMINDER_CREATE, IntentCategory.REMINDER_CREATE, RiskLevel.MEDIUM),
        (ActionType.ROUTINE_RUN_HIGH_IMPACT, IntentCategory.ROUTINE_RUN, RiskLevel.HIGH),
    ],
)
def test_medium_and_high_actions_require_confirmation(
    action_type: ActionType,
    intent_category: IntentCategory,
    risk_level: RiskLevel,
) -> None:
    with pytest.raises(ValueError, match="require confirmation"):
        ActionCandidate(
            action_id="act-medium",
            action_type=action_type,
            target="yarin 09:00",
            parameters={"time": "09:00"},
            source=ActionSource.TEXT,
            user_goal="Yarin hatirlat",
            intent_category=intent_category,
            risk_level=risk_level,
            requires_confirmation=False,
            dry_run_supported=True,
            reversible=True,
            expected_result="Hatirlatici olusturulur.",
        )


def test_ambiguous_intent_requires_clarification() -> None:
    intent = IntentResult(
        intent_id="intent-ambiguous",
        category=IntentCategory.AMBIGUOUS,
        confidence=0.45,
        language="tr",
        raw_text="Isigi ac",
        normalized_text="isigi ac",
        target="isik",
    )
    clarification = ClarificationRequest(
        reason="Target is ambiguous.",
        missing_fields=["room", "device_id"],
        candidate_targets=["salon", "calisma odasi", "yatak odasi"],
        suggested_questions=["Hangi isigi acmami istersin?"],
    )
    assert intent.requires_clarification is True
    assert clarification.safe_default == "no_action"


def test_action_preview_fields_and_blocked_behavior() -> None:
    preview = ActionPreview(
        action_id="act-preview",
        summary="Dosya silme engellendi.",
        target="report.docx",
        parameters_preview={"path": "report.docx"},
        risk_level=RiskLevel.BLOCKED,
        will_change_state=True,
        requires_confirmation=True,
        reversible=False,
        estimated_effect="Dosya silinirdi.",
        blocked_reason="file.delete is blocked.",
    )
    assert preview.safe_to_execute is False
    assert preview.requires_confirmation is False


def test_action_result_status_contract() -> None:
    result = ActionResult(
        action_id="act-result",
        status=ActionStatus.PREVIEWED,
        executed=False,
        dry_run=True,
        message="Preview produced.",
    )
    assert result.status == ActionStatus.PREVIEWED
    assert result.executed is False


def test_action_result_rejects_dry_run_execution() -> None:
    with pytest.raises(ValueError, match="dry-run"):
        ActionResult(
            action_id="act-invalid",
            status=ActionStatus.EXECUTED,
            executed=True,
            dry_run=True,
            message="invalid",
        )


def test_turkish_example_mapping_fixture() -> None:
    examples = [
        ("Chrome'u ac", IntentCategory.PC_OPEN_APP, ActionType.PC_OPEN_APP, RiskLevel.LOW),
        ("Bilgisayar durumunu goster", IntentCategory.PC_SYSTEM_INFO, ActionType.PC_SYSTEM_INFO, RiskLevel.SAFE_READONLY),
        ("Salon isigini ac", IntentCategory.DEVICE_TURN_ON, ActionType.DEVICE_TURN_ON, RiskLevel.MEDIUM),
        ("Evden cikiyorum rutinini baslat", IntentCategory.ROUTINE_RUN, ActionType.ROUTINE_RUN_HIGH_IMPACT, RiskLevel.HIGH),
        ("Su dosyayi sil", IntentCategory.BLOCKED, ActionType.FILE_DELETE, RiskLevel.BLOCKED),
    ]
    assert len(examples) == 5
    assert examples[0][2] == ActionType.PC_OPEN_APP
    assert examples[-1][3] == RiskLevel.BLOCKED
