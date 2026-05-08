from datetime import timedelta

from app.actions.types import ActionSource
from app.panel.models import PanelItemStatus, PanelItemType, PanelOperationStatus
from app.panel.policy import utcnow
from app.panel.service import PermissionPanelService
from app.panel.store import InMemoryPanelStore
import app.personal_assistant.store as personal_assistant_store


def build_service() -> PermissionPanelService:
    return PermissionPanelService(store=InMemoryPanelStore())


def test_store_add_list_get_and_clear() -> None:
    service = build_service()
    created = service.submit_text("Salon isigini ac")
    assert created.status is PanelOperationStatus.CREATED
    item_id = created.item.item_id
    listed = service.list_items()
    assert len(listed.items) == 1
    shown = service.show_item(item_id)
    assert shown.item.item_id == item_id
    cleared = service.clear_items()
    assert cleared.metadata["cleared_count"] == 1


def test_submit_home_confirmation_item() -> None:
    service = build_service()
    result = service.submit_text("Salon isigini ac")
    assert result.item.item_type is PanelItemType.CONFIRMATION_REQUIRED
    assert result.item.requires_confirmation is True


def test_submit_clarification_item() -> None:
    service = build_service()
    result = service.submit_text("Isigi ac")
    assert result.item.item_type is PanelItemType.CLARIFICATION_REQUIRED


def test_submit_blocked_item() -> None:
    service = build_service()
    result = service.submit_text("Sifrelerimi oku")
    assert result.item.item_type is PanelItemType.BLOCKED
    assert result.item.status is PanelItemStatus.BLOCKED


def test_submit_pc_preview_item() -> None:
    service = build_service()
    result = service.submit_text("Chrome'u ac")
    assert result.item.item_type is PanelItemType.ACTION_PREVIEW


def test_approve_item_does_not_execute() -> None:
    service = build_service()
    created = service.submit_text("Salon isigini ac")
    approved = service.approve_item(created.item.item_id)
    assert approved.status is PanelOperationStatus.APPROVED
    assert approved.decision.execution_attempted is False
    assert approved.decision.execution_allowed is False


def test_blocked_item_cannot_be_approved() -> None:
    service = build_service()
    created = service.submit_text("Sifrelerimi oku")
    approved = service.approve_item(created.item.item_id)
    assert approved.status is PanelOperationStatus.BLOCKED


def test_clarification_item_cannot_be_approved() -> None:
    service = build_service()
    created = service.submit_text("Isigi ac")
    approved = service.approve_item(created.item.item_id)
    assert approved.status is PanelOperationStatus.BLOCKED


def test_deny_cancel_update_status() -> None:
    service = build_service()
    created = service.submit_text("Salon isigini ac", source=ActionSource.TEXT)
    denied = service.deny_item(created.item.item_id)
    assert denied.item.status is PanelItemStatus.DENIED

    created_2 = service.submit_text("Chrome'u ac")
    cancelled = service.cancel_item(created_2.item.item_id)
    assert cancelled.item.status is PanelItemStatus.CANCELLED


def test_expired_item_cannot_be_approved() -> None:
    service = build_service()
    created = service.submit_text("Salon isigini ac")
    created.item.expires_at = utcnow() - timedelta(seconds=5)
    service.store.update(created.item)
    approved = service.approve_item(created.item.item_id)
    assert approved.status is PanelOperationStatus.BLOCKED
    assert "süresi doldu" in approved.message.lower()


def test_cancelled_item_cannot_be_approved() -> None:
    service = build_service()
    created = service.submit_text("Chrome'u ac")
    service.cancel_item(created.item.item_id)
    approved = service.approve_item(created.item.item_id)
    assert approved.status is PanelOperationStatus.BLOCKED
    assert "approve edilemez" in approved.message.lower()


def test_denied_item_cannot_be_approved() -> None:
    service = build_service()
    created = service.submit_text("Salon isigini ac", source=ActionSource.TEXT)
    service.deny_item(created.item.item_id)
    approved = service.approve_item(created.item.item_id)
    assert approved.status is PanelOperationStatus.BLOCKED
    assert "reddedilen" in approved.message.lower()


def test_submit_reminder_confirmation_item(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(personal_assistant_store, "_default_store_path", lambda: tmp_path / "personal-assistant.json")
    personal_assistant_store._global_store = None
    service = build_service()
    result = service.submit_text("Bana 20 dakika sonra su icmeyi hatirlat")
    assert result.item.item_type is PanelItemType.CONFIRMATION_REQUIRED
    assert "Hatırlatıcı" in result.item.title


def test_approve_reminder_item_does_not_schedule_real_reminder(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(personal_assistant_store, "_default_store_path", lambda: tmp_path / "personal-assistant.json")
    personal_assistant_store._global_store = None
    service = build_service()
    created = service.submit_text("Bana 20 dakika sonra su icmeyi hatirlat")
    approved = service.approve_item(created.item.item_id)
    assert approved.status is PanelOperationStatus.APPROVED
    assert approved.decision.execution_attempted is False
    assert approved.decision.execution_allowed is False
