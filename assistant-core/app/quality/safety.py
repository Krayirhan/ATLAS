from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable, Iterator

from app.actions.intent_router import IntentRouter
from app.actions.types import ActionSource
from app.control.pc_adapter import PCControlAdapter
from app.conversation.loop import ConversationLoop
from app.conversation.models import ConversationResponseType
from app.demo.runner import DemoRunner
from app.devices.planner import DeviceActionPlanner
from app.devices.registry import DeviceRegistry
from app.home.service import HomeControlService
from app.panel.service import PermissionPanelService
from app.personal_assistant.calendar import CalendarService
from app.personal_assistant.notifications import NotificationService
from app.personal_assistant.reminders import ReminderService
from app.quality.models import (
    SAFETY_INVARIANT_FLAGS,
    SAFETY_INVARIANT_EXPECTED,
    SafetyInvariantCheck,
    SafetyInvariantReport,
)
from app.routines.service import RoutineService
from app.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
from app.voice.models import VoicePipelineRequest, VoiceSource
from app.voice.pipeline import VoicePipeline


DEFAULT_INVARIANT_FLAGS: dict[str, bool] = dict(SAFETY_INVARIANT_EXPECTED)


def normalize_flags(*payloads: dict[str, Any] | None) -> dict[str, bool]:
    flags = dict(DEFAULT_INVARIANT_FLAGS)
    for payload in payloads:
        if not payload:
            continue
        for flag in SAFETY_INVARIANT_FLAGS:
            if flag in payload:
                flags[flag] = bool(payload[flag])
    return flags


def validate_invariant_flags(flags: dict[str, bool]) -> list[str]:
    problems: list[str] = []
    for flag, expected in SAFETY_INVARIANT_EXPECTED.items():
        actual = bool(flags.get(flag, False))
        if actual != expected:
            problems.append(f"{flag} expected {str(expected).lower()} but got {str(actual).lower()}.")
    return problems


@contextmanager
def isolated_preview_state() -> Iterator[None]:
    from app.conversation import state as conversation_state
    from app.personal_assistant import store as personal_store

    original_panel_store = os.environ.get("ATLAS_PANEL_STORE_PATH")
    original_personal_store = personal_store._global_store
    original_state_manager = conversation_state._global_state_manager

    with TemporaryDirectory(prefix="atlas-hardening-") as temp_dir:
        temp_path = Path(temp_dir)
        os.environ["ATLAS_PANEL_STORE_PATH"] = str(temp_path / "panel.json")
        personal_store._global_store = personal_store.InMemoryAssistantStore()
        conversation_state._global_state_manager = conversation_state.StateManager()
        try:
            yield
        finally:
            if original_panel_store is None:
                os.environ.pop("ATLAS_PANEL_STORE_PATH", None)
            else:
                os.environ["ATLAS_PANEL_STORE_PATH"] = original_panel_store
            personal_store._global_store = original_personal_store
            conversation_state._global_state_manager = original_state_manager


def _build_check(
    *,
    name: str,
    command_surface: str,
    flags: dict[str, bool],
    warnings: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
    extra_errors: list[str] | None = None,
) -> SafetyInvariantCheck:
    problems = validate_invariant_flags(flags)
    if extra_errors:
        problems.extend(extra_errors)
    combined_warnings = list(warnings or [])
    combined_warnings.extend(problems)
    return SafetyInvariantCheck(
        name=name,
        command_surface=command_surface,
        passed=not problems,
        flags=flags,
        warnings=combined_warnings,
        metadata=metadata or {},
    )


def probe_chat_preview(project_name: str) -> SafetyInvariantCheck:
    loop = ConversationLoop()
    response = loop.handle_text("Chrome'u aç", project_name=project_name, source=ActionSource.TEXT)
    flags = normalize_flags(response.audit_metadata)
    extra_errors: list[str] = []
    if response.response_type is not ConversationResponseType.ACTION_PREVIEW:
        extra_errors.append(f"Beklenen response_type=action_preview, gelen={response.response_type.value}.")
    if response.pc_plan is None or response.pc_plan.dry_run is not True:
        extra_errors.append("PC onizleme plani dry_run modunda olmalidir.")
    return _build_check(
        name="chat_preview",
        command_surface='ai chat "Chrome\'u aç"',
        flags=flags,
        warnings=list(response.warnings),
        metadata={"response_type": response.response_type.value},
        extra_errors=extra_errors,
    )


def probe_voice_preview(project_name: str) -> SafetyInvariantCheck:
    pipeline = VoicePipeline(MockSTTAdapter(), MockTTSAdapter())
    result = pipeline.handle(
        VoicePipelineRequest(
            project_name=project_name,
            mock_transcript="Salon ışığını aç",
            source=VoiceSource.MOCK_TRANSCRIPT,
        )
    )
    response_type = result.conversation_response.response_type.value if result.conversation_response else "none"
    flags = normalize_flags(result.metadata, {
        "audio_retained": result.audio_retained,
        "microphone_used": result.microphone_used,
        "wake_word_used": result.wake_word_used,
        "execution_attempted": result.execution_attempted,
    })
    extra_errors: list[str] = []
    if result.conversation_response is None:
        extra_errors.append("Voice pipeline bir conversation response dondurmelidir.")
    elif result.conversation_response.response_type is not ConversationResponseType.CONFIRMATION_REQUIRED:
        extra_errors.append(
            f"Beklenen response_type=confirmation_required, gelen={result.conversation_response.response_type.value}."
        )
    return _build_check(
        name="voice_mock_preview",
        command_surface='ai voice --mock-transcript "Salon ışığını aç"',
        flags=flags,
        warnings=list(result.safety_warnings),
        metadata={"response_type": response_type},
        extra_errors=extra_errors,
    )


def probe_routine_preview(project_name: str) -> SafetyInvariantCheck:
    service = RoutineService()
    result = service.handle_text("Çalışma modunu başlat")
    audit_metadata = getattr(result, "audit_metadata", {}) if result is not None else {}
    flags = normalize_flags(audit_metadata)
    extra_errors: list[str] = []
    if result is None:
        extra_errors.append("Routine sonucu bos dondu.")
    elif getattr(getattr(result, "status", None), "value", "") != "awaiting_confirmation":
        extra_errors.append("Routine medium risk akista awaiting_confirmation olmalidir.")
    return _build_check(
        name="routine_preview",
        command_surface='ai routine "Çalışma modunu başlat"',
        flags=flags,
        metadata={"status": getattr(getattr(result, "status", None), "value", "none")},
        extra_errors=extra_errors,
    )


def probe_reminder_preview(project_name: str) -> SafetyInvariantCheck:
    service = ReminderService()
    result = service.create_reminder("Bana 20 dakika sonra su içmeyi hatırlat")
    flags = normalize_flags(result.audit_metadata)
    extra_errors: list[str] = []
    if result.status.value != "pending_confirmation":
        extra_errors.append("Hatirlatici preview akisi pending_confirmation olmalidir.")
    return _build_check(
        name="reminder_preview",
        command_surface='ai reminder "Bana 20 dakika sonra su içmeyi hatırlat"',
        flags=flags,
        warnings=list(result.warnings),
        metadata={"status": result.status.value},
        extra_errors=extra_errors,
    )


def probe_calendar_preview(project_name: str) -> SafetyInvariantCheck:
    service = CalendarService()
    result = service.create_event_draft("Yarın 10'a toplantı ekle")
    flags = normalize_flags(result.audit_metadata)
    extra_errors: list[str] = []
    if result.status.value != "pending_confirmation":
        extra_errors.append("Takvim taslagi pending_confirmation olmalidir.")
    return _build_check(
        name="calendar_preview",
        command_surface='ai calendar "Yarın 10\'a toplantı ekle"',
        flags=flags,
        warnings=list(result.warnings),
        metadata={"status": result.status.value},
        extra_errors=extra_errors,
    )


def probe_notification_preview(project_name: str) -> SafetyInvariantCheck:
    result = NotificationService().build_notification_preview(
        title="ATLAS Hatırlatma",
        body="Su içme zamanı",
    )
    flags = normalize_flags(result.audit_metadata)
    return _build_check(
        name="notification_preview",
        command_surface='ai notification-preview --title "ATLAS Hatırlatma"',
        flags=flags,
        warnings=list(result.warnings),
        metadata={"status": result.status.value},
    )


def probe_panel_submit(project_name: str) -> SafetyInvariantCheck:
    service = PermissionPanelService()
    result = service.submit_text("Salon ışığını aç", source=ActionSource.TEXT, project_name=project_name)
    flags = normalize_flags(result.item.audit_metadata if result.item is not None else {}, {
        "execution_attempted": result.decision.execution_attempted if result.decision is not None else False,
    })
    extra_errors: list[str] = []
    if result.item is None:
        extra_errors.append("Panel submit bir item uretmelidir.")
    elif result.item.item_type.value != "confirmation_required":
        extra_errors.append("Panel submit sonucu confirmation_required item olmalidir.")
    return _build_check(
        name="panel_submit_preview",
        command_surface='ai panel --submit "Salon ışığını aç"',
        flags=flags,
        warnings=list(result.warnings),
        metadata={"status": result.status.value, "item_status": result.item.status.value if result.item else "none"},
        extra_errors=extra_errors,
    )


def probe_panel_approve(project_name: str) -> SafetyInvariantCheck:
    service = PermissionPanelService()
    created = service.submit_text("Salon ışığını aç", source=ActionSource.TEXT, project_name=project_name)
    approved = service.approve_item(created.item.item_id) if created.item is not None else None
    decision = approved.decision if approved is not None else None
    flags = normalize_flags(
        created.item.audit_metadata if created.item is not None else {},
        {"execution_attempted": decision.execution_attempted if decision is not None else False},
    )
    extra_errors: list[str] = []
    if approved is None:
        extra_errors.append("Panel approve sonucu olusmadi.")
    elif approved.status.value != "approved":
        extra_errors.append(f"Panel approve beklenen approved, gelen={approved.status.value}.")
    elif decision is None:
        extra_errors.append("Panel approve karari kaydedilmelidir.")
    else:
        if decision.execution_allowed:
            extra_errors.append("Panel approve execution_allowed=true yapmamali.")
        if decision.execution_attempted:
            extra_errors.append("Panel approve execution_attempted=true yapmamali.")
    return _build_check(
        name="panel_approve_no_execution",
        command_surface='ai panel --approve <item_id>',
        flags=flags,
        warnings=list(approved.warnings) if approved is not None else [],
        metadata={"status": approved.status.value if approved is not None else "missing"},
        extra_errors=extra_errors,
    )


def probe_home_preview(project_name: str) -> SafetyInvariantCheck:
    _, result = HomeControlService().preview_plan("Salon ışığını aç", source=ActionSource.TEXT)
    flags = normalize_flags(result.audit_metadata)
    extra_errors: list[str] = []
    if result.status.value != "awaiting_confirmation":
        extra_errors.append("Home preview sonucu awaiting_confirmation olmalidir.")
    return _build_check(
        name="home_preview",
        command_surface='ai home-preview "Salon ışığını aç"',
        flags=flags,
        metadata={"status": result.status.value},
        extra_errors=extra_errors,
    )


def probe_pc_preview(project_name: str) -> SafetyInvariantCheck:
    router = IntentRouter()
    adapter = PCControlAdapter()
    preview = router.preview("Chrome'u aç", source=ActionSource.TEXT)
    extra_errors: list[str] = []
    flags = normalize_flags(preview.permission_decision.audit_metadata if preview.permission_decision else {})
    if preview.action_candidate is None or preview.permission_decision is None:
        extra_errors.append("PC preview icin action candidate ve permission decision olusmalidir.")
    else:
        plan = adapter.build_plan(preview.action_candidate, preview.permission_decision, dry_run=True)
        result = adapter.execute(plan)
        flags = normalize_flags(preview.permission_decision.audit_metadata, result.audit_metadata)
        if result.executed:
            extra_errors.append("PC preview executed=true olmamali.")
        if result.status.value not in {"previewed", "blocked"}:
            extra_errors.append(f"PC preview beklenmeyen status dondu: {result.status.value}.")
    return _build_check(
        name="pc_preview",
        command_surface='ai pc-preview "Chrome\'u aç"',
        flags=flags,
        metadata={
            "intent": preview.intent.category.value if preview.intent else "none",
            "result_status": result.status.value if preview.action_candidate and preview.permission_decision else "missing",
        },
        extra_errors=extra_errors,
    )


def probe_device_preview(project_name: str) -> SafetyInvariantCheck:
    planner = DeviceActionPlanner(registry=DeviceRegistry())
    result = planner.preview_device_action("Salon ışığını aç", source=ActionSource.TEXT)
    plan_flags = result.plan.audit_metadata if result.plan is not None else {}
    flags = normalize_flags(result.metadata, plan_flags)
    extra_errors: list[str] = []
    if result.status.value != "planned":
        extra_errors.append(f"Device preview planned olmali, gelen={result.status.value}.")
    return _build_check(
        name="device_preview",
        command_surface='ai device "Salon ışığını aç"',
        flags=flags,
        warnings=list(result.warnings),
        metadata={"status": result.status.value},
        extra_errors=extra_errors,
    )


def probe_demo_all(project_name: str) -> SafetyInvariantCheck:
    report = DemoRunner(project_name=project_name).run_all()
    flags = normalize_flags(report.safety_summary.get("execution_boundary", {}))
    extra_errors: list[str] = []
    if report.failed_scenarios:
        extra_errors.append(f"Demo raporunda {report.failed_scenarios} basarisiz scenario var.")
    violations = report.safety_summary.get("violations", [])
    extra_errors.extend([f"Demo safety violation: {item['violation']}" for item in violations])
    return _build_check(
        name="demo_all_scenarios",
        command_surface="ai demo --all --show-safety",
        flags=flags,
        metadata={
            "total_scenarios": report.total_scenarios,
            "passed_scenarios": report.passed_scenarios,
        },
        extra_errors=extra_errors,
    )


SAFETY_PROBES: tuple[Callable[[str], SafetyInvariantCheck], ...] = (
    probe_chat_preview,
    probe_voice_preview,
    probe_routine_preview,
    probe_reminder_preview,
    probe_calendar_preview,
    probe_notification_preview,
    probe_panel_submit,
    probe_panel_approve,
    probe_home_preview,
    probe_pc_preview,
    probe_device_preview,
    probe_demo_all,
)


def run_safety_suite(project_name: str = "ATLAS") -> SafetyInvariantReport:
    checks: list[SafetyInvariantCheck] = []
    for probe in SAFETY_PROBES:
        with isolated_preview_state():
            checks.append(probe(project_name))

    passed = sum(1 for item in checks if item.passed)
    failed = len(checks) - passed
    recommendations: list[str] = []
    if failed:
        recommendations.append("Basarisiz safety check'lerde preview/runtime sinirini tekrar sikilastir.")
    else:
        recommendations.append("Tum safety invariant kontrolleri preview-only siniri icinde kaldi.")
    recommendations.append("Gercek PC, home, calendar, notification, microphone, wake word ve shell execution kapali kalmali.")

    return SafetyInvariantReport(
        total_checks=len(checks),
        passed=passed,
        failed=failed,
        checks=checks,
        recommendations=recommendations,
    )
