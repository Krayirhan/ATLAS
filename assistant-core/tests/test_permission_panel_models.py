from app.panel.models import (
    PanelDecision,
    PanelDecisionType,
    PanelItemStatus,
    PanelItemType,
    PermissionPanelItem,
    PermissionPanelState,
)


def test_permission_panel_item_builds() -> None:
    item = PermissionPanelItem(
        item_id="panel-1",
        item_type=PanelItemType.CONFIRMATION_REQUIRED,
        status=PanelItemStatus.PENDING,
        title="Onay",
        summary="Preview",
        user_message="Salon isigini ac",
    )
    assert item.item_id == "panel-1"


def test_panel_decision_builds() -> None:
    decision = PanelDecision(
        decision_id="decision-1",
        item_id="panel-1",
        decision=PanelDecisionType.APPROVE,
        user_confirmed=True,
    )
    assert decision.execution_attempted is False


def test_permission_panel_state_builds() -> None:
    state = PermissionPanelState(
        pending_count=1,
        blocked_count=0,
        approved_count=0,
        denied_count=0,
        cancelled_count=0,
    )
    assert state.pending_count == 1
