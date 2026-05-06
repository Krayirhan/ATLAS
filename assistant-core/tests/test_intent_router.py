from __future__ import annotations

from app.actions import ActionSource, ActionType, IntentCategory, IntentRouter, PermissionStatus, RiskLevel


def test_chrome_open_maps_to_pc_open_app() -> None:
    preview = IntentRouter().preview("Chrome'u ac")
    assert preview.intent.category is IntentCategory.PC_OPEN_APP
    assert preview.action_candidate is not None
    assert preview.action_candidate.action_type is ActionType.PC_OPEN_APP
    assert preview.action_candidate.target == "Chrome"
    assert preview.action_candidate.risk_level is RiskLevel.LOW
    assert preview.permission_decision is not None
    assert preview.permission_decision.status is PermissionStatus.PREVIEW_ALLOWED


def test_not_defteri_maps_to_pc_open_app() -> None:
    intent = IntentRouter().parse_text("Not Defteri'ni ac")
    assert intent.category is IntentCategory.PC_OPEN_APP
    assert intent.target == "Not Defteri"


def test_belgeler_klasoru_maps_to_open_folder() -> None:
    preview = IntentRouter().preview("Belgeler klasorunu ac")
    assert preview.intent.category is IntentCategory.PC_OPEN_FOLDER
    assert preview.action_candidate is not None
    assert preview.action_candidate.action_type is ActionType.PC_OPEN_FOLDER


def test_bilgisayar_bilgileri_maps_to_system_info() -> None:
    preview = IntentRouter().preview("Bilgisayar bilgilerini goster")
    assert preview.intent.category is IntentCategory.PC_SYSTEM_INFO
    assert preview.action_candidate is not None
    assert preview.action_candidate.risk_level is RiskLevel.SAFE_READONLY
    assert preview.permission_decision is not None
    assert preview.permission_decision.status is PermissionStatus.SAFE_READONLY


def test_pdf_dosyalari_maps_to_file_search() -> None:
    preview = IntentRouter().preview("PDF dosyalarimi bul")
    assert preview.intent.category is IntentCategory.FILE_SEARCH
    assert preview.action_candidate is not None
    assert preview.action_candidate.action_type is ActionType.FILE_SEARCH
    assert preview.action_candidate.risk_level is RiskLevel.SAFE_READONLY


def test_google_search_maps_to_browser_search() -> None:
    preview = IntentRouter().preview("Google'da hava durumunu ara")
    assert preview.intent.category is IntentCategory.BROWSER_SEARCH
    assert preview.action_candidate is not None
    assert preview.action_candidate.action_type is ActionType.BROWSER_SEARCH


def test_reminder_maps_to_medium_confirmation() -> None:
    preview = IntentRouter().preview("Bana 20 dakika sonra su icmeyi hatirlat")
    assert preview.intent.category is IntentCategory.REMINDER_CREATE
    assert preview.action_candidate is not None
    assert preview.action_candidate.risk_level is RiskLevel.MEDIUM
    assert preview.permission_decision is not None
    assert preview.permission_decision.status is PermissionStatus.CONFIRMATION_REQUIRED


def test_routine_maps_to_medium_confirmation() -> None:
    preview = IntentRouter().preview("Calisma modunu baslat")
    assert preview.intent.category is IntentCategory.ROUTINE_RUN
    assert preview.action_candidate is not None
    assert preview.action_candidate.action_type is ActionType.ROUTINE_RUN
    assert preview.permission_decision is not None
    assert preview.permission_decision.status is PermissionStatus.CONFIRMATION_REQUIRED


def test_device_turn_on_maps_to_confirmation_required() -> None:
    preview = IntentRouter().preview("Salon isigini ac")
    assert preview.intent.category is IntentCategory.DEVICE_TURN_ON
    assert preview.action_candidate is not None
    assert preview.action_candidate.action_type is ActionType.DEVICE_TURN_ON
    assert preview.permission_decision is not None
    assert preview.permission_decision.status is PermissionStatus.CONFIRMATION_REQUIRED


def test_isigi_ac_requires_clarification() -> None:
    preview = IntentRouter().preview("Isigi ac")
    assert preview.intent.category is IntentCategory.AMBIGUOUS
    assert preview.intent.requires_clarification is True
    assert preview.permission_decision is not None
    assert preview.permission_decision.status is PermissionStatus.CLARIFICATION_REQUIRED


def test_kapat_requires_clarification() -> None:
    preview = IntentRouter().preview("Kapat")
    assert preview.intent.category is IntentCategory.AMBIGUOUS
    assert preview.clarification is not None


def test_shutdown_maps_to_high_confirmation() -> None:
    preview = IntentRouter().preview("Bilgisayari kapat")
    assert preview.action_candidate is not None
    assert preview.action_candidate.action_type is ActionType.PC_SHUTDOWN
    assert preview.action_candidate.risk_level is RiskLevel.HIGH
    assert preview.permission_decision is not None
    assert preview.permission_decision.status is PermissionStatus.CONFIRMATION_REQUIRED


def test_blocked_file_delete_maps_to_blocked() -> None:
    preview = IntentRouter().preview("Su dosyayi sil")
    assert preview.intent.category is IntentCategory.BLOCKED
    assert preview.action_candidate is not None
    assert preview.action_candidate.action_type is ActionType.FILE_DELETE
    assert preview.permission_decision is not None
    assert preview.permission_decision.status is PermissionStatus.BLOCKED


def test_secret_read_maps_to_blocked() -> None:
    preview = IntentRouter().preview("Sifrelerimi oku")
    assert preview.intent.category is IntentCategory.BLOCKED
    assert preview.action_candidate is not None
    assert preview.action_candidate.action_type is ActionType.SECRET_READ
    assert preview.permission_decision is not None
    assert preview.permission_decision.status is PermissionStatus.BLOCKED


def test_unknown_text_returns_clarification_without_execution() -> None:
    preview = IntentRouter().preview("Bana garip bir sey yap")
    assert preview.intent.category is IntentCategory.UNKNOWN
    assert preview.action_candidate is None
    assert preview.clarification is not None
    assert preview.permission_decision is None


def test_voice_medium_action_requires_confirmation() -> None:
    preview = IntentRouter().preview("Salon isigini ac", source=ActionSource.VOICE)
    assert preview.permission_decision is not None
    assert preview.permission_decision.status is PermissionStatus.CONFIRMATION_REQUIRED
    assert preview.permission_decision.confirmation_prompt.startswith("Sesli komut")


def test_voice_high_action_requires_confirmation_and_warning() -> None:
    preview = IntentRouter().preview("Bilgisayari kapat", source=ActionSource.VOICE)
    assert preview.permission_decision is not None
    assert preview.permission_decision.status is PermissionStatus.CONFIRMATION_REQUIRED
    assert preview.permission_decision.warnings


def test_preview_produces_permission_decision_without_execution() -> None:
    preview = IntentRouter().preview("Chrome'u ac")
    assert preview.permission_decision is not None
    assert preview.permission_decision.audit_metadata["execution_attempted"] is False
