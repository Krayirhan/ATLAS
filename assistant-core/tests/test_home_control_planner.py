from __future__ import annotations

from app.actions import ActionSource
from app.home.models import HomeControlStatus
from app.home.planner import HomeControlPlanner
from app.home.service import HomeControlService


def test_home_planner_light_turn_on_confirmation_required() -> None:
    result = HomeControlPlanner().preview_from_text("Salon isigini ac")
    assert result.status is HomeControlStatus.AWAITING_CONFIRMATION
    assert result.executed is False
    assert result.audit_metadata["execution_attempted"] is False


def test_home_planner_thermostat_write_confirmation_required() -> None:
    result = HomeControlPlanner().preview_from_text("Klimayi 24 derece yap")
    assert result.status is HomeControlStatus.AWAITING_CONFIRMATION
    assert result.executed is False


def test_home_planner_ambiguous_light_is_unsupported() -> None:
    result = HomeControlPlanner().preview_from_text("Isigi ac")
    assert result.status is HomeControlStatus.UNSUPPORTED
    assert result.executed is False


def test_home_planner_camera_is_blocked() -> None:
    result = HomeControlPlanner().preview_from_text("Kamerayi ac")
    assert result.status is HomeControlStatus.BLOCKED


def test_home_planner_state_query_is_state_read() -> None:
    service = HomeControlService()
    plan, result = service.preview_plan("Salon isigi acik mi")
    assert plan is not None
    assert plan.state_read is True
    assert plan.state_write is False
    assert result.status is HomeControlStatus.STATE_READ


def test_home_planner_safe_to_execute_false() -> None:
    service = HomeControlService()
    plan, result = service.preview_plan("Salon isigini ac")
    assert plan is not None
    assert plan.safe_to_execute is False
    assert plan.dry_run is True
    assert result.executed is False


def test_home_service_preview_text_voice_source_respects_preview_only() -> None:
    result = HomeControlService().preview_text("Salon isigini ac", source=ActionSource.VOICE)
    assert result.status is HomeControlStatus.AWAITING_CONFIRMATION
    assert result.audit_metadata["execution_attempted"] is False
