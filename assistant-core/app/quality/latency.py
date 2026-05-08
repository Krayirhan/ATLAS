from __future__ import annotations

from time import perf_counter

from app.quality.models import LatencyMeasurement, LatencyReport
from app.quality.safety import (
    isolated_preview_state,
    probe_calendar_preview,
    probe_chat_preview,
    probe_demo_all,
    probe_home_preview,
    probe_panel_submit,
    probe_reminder_preview,
    probe_routine_preview,
    probe_voice_preview,
)


LATENCY_THRESHOLDS_MS: dict[str, int] = {
    "ai_chat": 1500,
    "ai_voice": 2500,
    "ai_routine": 1500,
    "ai_reminder": 1500,
    "ai_calendar": 1500,
    "ai_panel": 1500,
    "ai_home_preview": 1500,
    "ai_demo_all": 7000,
}


def _measure(name: str, command_surface: str, threshold_ms: int, probe, project_name: str) -> LatencyMeasurement:
    with isolated_preview_state():
        started = perf_counter()
        check = probe(project_name)
        duration_ms = int((perf_counter() - started) * 1000)

    warnings = list(check.warnings)
    if not check.passed:
        warnings.append("Latency olcumu sirasinda safety invariant ihlali tespit edildi.")
    passed = duration_ms <= threshold_ms and check.passed
    if duration_ms > threshold_ms:
        warnings.append(f"Threshold asildi: {duration_ms}ms > {threshold_ms}ms.")

    return LatencyMeasurement(
        name=name,
        command_surface=command_surface,
        duration_ms=duration_ms,
        threshold_ms=threshold_ms,
        passed=passed,
        warnings=warnings,
        metadata={
            "safety_flags": check.flags,
            "safety_passed": check.passed,
            "safety_metadata": check.metadata,
        },
    )


def run_latency_suite(project_name: str = "ATLAS") -> LatencyReport:
    measurements = [
        _measure("chat_chrome_open", 'ai chat "Chrome\'u aç"', LATENCY_THRESHOLDS_MS["ai_chat"], probe_chat_preview, project_name),
        _measure("voice_home_preview", 'ai voice --mock-transcript "Salon ışığını aç"', LATENCY_THRESHOLDS_MS["ai_voice"], probe_voice_preview, project_name),
        _measure("routine_work_mode", 'ai routine "Çalışma modunu başlat"', LATENCY_THRESHOLDS_MS["ai_routine"], probe_routine_preview, project_name),
        _measure("reminder_create", 'ai reminder "Bana 20 dakika sonra su içmeyi hatırlat"', LATENCY_THRESHOLDS_MS["ai_reminder"], probe_reminder_preview, project_name),
        _measure("calendar_draft", 'ai calendar "Yarın 10\'a toplantı ekle"', LATENCY_THRESHOLDS_MS["ai_calendar"], probe_calendar_preview, project_name),
        _measure("panel_submit", 'ai panel --submit "Salon ışığını aç"', LATENCY_THRESHOLDS_MS["ai_panel"], probe_panel_submit, project_name),
        _measure("home_preview", 'ai home-preview "Salon ışığını aç"', LATENCY_THRESHOLDS_MS["ai_home_preview"], probe_home_preview, project_name),
        _measure("demo_all", "ai demo --all --no-write", LATENCY_THRESHOLDS_MS["ai_demo_all"], probe_demo_all, project_name),
    ]
    passed = sum(1 for item in measurements if item.passed)
    failed = len(measurements) - passed
    recommendations: list[str] = []
    if failed:
        recommendations.append("Threshold asan surface'lerde ekstra gereksiz state veya formatting isini azalt.")
    else:
        recommendations.append("Tum latency olcumleri Sprint 51 hedef esiklerinin icinde kaldi.")
    recommendations.append("Olcumler deterministic preview modullerinde yapildi; gercek execution acilmadi.")

    return LatencyReport(
        total_measurements=len(measurements),
        passed=passed,
        failed=failed,
        measurements=measurements,
        recommendations=recommendations,
    )
