from __future__ import annotations

from app.quality.models import SAFETY_INVARIANT_EXPECTED
from app.quality.safety import run_safety_suite


def test_safety_suite_passes_all_checks() -> None:
    report = run_safety_suite("ATLAS")
    assert report.failed == 0, report.model_dump()
    assert report.passed == report.total_checks


def test_safety_suite_keeps_all_invariants_false() -> None:
    report = run_safety_suite("ATLAS")
    for check in report.checks:
        for flag, expected in SAFETY_INVARIANT_EXPECTED.items():
            assert check.flags[flag] is expected, f"{check.name}: {flag} expected {expected}"


def test_safety_suite_covers_required_surfaces() -> None:
    report = run_safety_suite("ATLAS")
    names = {check.name for check in report.checks}
    assert {
        "demo_all_scenarios",
        "voice_mock_preview",
        "home_preview",
        "panel_approve_no_execution",
        "reminder_preview",
        "calendar_preview",
        "routine_preview",
        "pc_preview",
        "device_preview",
        "notification_preview",
    }.issubset(names)
