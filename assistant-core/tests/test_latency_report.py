from __future__ import annotations

from app.quality.latency import LATENCY_THRESHOLDS_MS, run_latency_suite
from app.quality.models import LatencyMeasurement
from app.quality.report import build_json


def test_latency_measurement_model_works() -> None:
    measurement = LatencyMeasurement(
        name="chat",
        command_surface='ai chat "Chrome\'u aç"',
        duration_ms=123,
        threshold_ms=1500,
        passed=True,
        warnings=[],
        metadata={"execution_attempted": False},
    )
    assert measurement.duration_ms == 123
    assert measurement.threshold_ms == 1500
    assert measurement.passed is True


def test_latency_report_can_be_produced() -> None:
    report = run_latency_suite("ATLAS")
    assert report.total_measurements == 8
    assert report.passed + report.failed == report.total_measurements
    assert build_json(
        __import__("app.quality.models", fromlist=["HardeningReport"]).HardeningReport(
            project_name="ATLAS",
            modes=["latency"],
            latency_report=report,
        )
    )


def test_latency_thresholds_and_no_real_execution() -> None:
    report = run_latency_suite("ATLAS")
    thresholds = {
        "chat_chrome_open": LATENCY_THRESHOLDS_MS["ai_chat"],
        "voice_home_preview": LATENCY_THRESHOLDS_MS["ai_voice"],
        "routine_work_mode": LATENCY_THRESHOLDS_MS["ai_routine"],
        "reminder_create": LATENCY_THRESHOLDS_MS["ai_reminder"],
        "calendar_draft": LATENCY_THRESHOLDS_MS["ai_calendar"],
        "panel_submit": LATENCY_THRESHOLDS_MS["ai_panel"],
        "home_preview": LATENCY_THRESHOLDS_MS["ai_home_preview"],
        "demo_all": LATENCY_THRESHOLDS_MS["ai_demo_all"],
    }
    for measurement in report.measurements:
        assert measurement.threshold_ms == thresholds[measurement.name]
        safety_flags = measurement.metadata["safety_flags"]
        assert safety_flags["execution_attempted"] is False
        assert safety_flags["shell_used"] is False
