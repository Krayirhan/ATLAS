"""Tests for DemoRunner (Sprint 50)."""

import pytest

from app.demo.models import DemoCategory, DemoReport, DemoResult
from app.demo.policy import validate_safety
from app.demo.runner import DemoRunner


@pytest.fixture()
def runner() -> DemoRunner:
    return DemoRunner(project_name="ATLAS")


def test_list_scenarios(runner: DemoRunner):
    scenarios = runner.list_scenarios()
    assert len(scenarios) >= 12


# --- Individual scenario runs ---

def test_run_chat_chrome_open(runner: DemoRunner):
    result = runner.run_scenario("chat_chrome_open")
    assert result.passed, f"chat_chrome_open failed: {result.warnings}"
    assert result.assistant_message


def test_run_ambiguous_light(runner: DemoRunner):
    result = runner.run_scenario("ambiguous_light")
    assert result.passed, f"ambiguous_light failed: {result.warnings}"


def test_run_blocked_secret(runner: DemoRunner):
    result = runner.run_scenario("blocked_secret")
    assert result.passed, f"blocked_secret failed: {result.warnings}"
    assert result.response_type == "blocked"


def test_run_voice_home_preview(runner: DemoRunner):
    result = runner.run_scenario("voice_home_preview")
    assert result.passed, f"voice_home_preview failed: {result.warnings}"
    assert result.safety_flags.get("microphone_used") is False
    assert result.safety_flags.get("wake_word_used") is False
    assert result.safety_flags.get("audio_retained") is False


def test_run_reminder_create(runner: DemoRunner):
    result = runner.run_scenario("reminder_create")
    assert result.passed, f"reminder_create failed: {result.warnings}"
    assert result.safety_flags.get("os_notification_sent") is False


def test_run_calendar_draft(runner: DemoRunner):
    result = runner.run_scenario("calendar_draft")
    assert result.passed, f"calendar_draft failed: {result.warnings}"
    assert result.safety_flags.get("external_calendar_used") is False


def test_run_memory_preference_store(runner: DemoRunner):
    result = runner.run_scenario("memory_preference_store")
    assert result.passed, f"memory_preference_store failed: {result.warnings}"


def test_run_memory_sensitive_blocked(runner: DemoRunner):
    result = runner.run_scenario("memory_sensitive_blocked")
    assert result.passed, f"memory_sensitive_blocked failed: {result.warnings}"
    assert result.response_type == "blocked"


def test_run_home_salon_light(runner: DemoRunner):
    result = runner.run_scenario("home_salon_light")
    assert result.passed, f"home_salon_light failed: {result.warnings}"
    assert result.safety_flags.get("physical_device_touched") is False


def test_run_home_climate_preview(runner: DemoRunner):
    result = runner.run_scenario("home_climate_preview")
    assert result.passed, f"home_climate_preview failed: {result.warnings}"


def test_run_calendar_query(runner: DemoRunner):
    result = runner.run_scenario("calendar_query")
    assert result.passed, f"calendar_query failed: {result.warnings}"
    assert result.safety_flags.get("external_calendar_used") is False


def test_run_panel_queue_light(runner: DemoRunner):
    result = runner.run_scenario("panel_queue_light")
    assert result.passed, f"panel_queue_light failed: {result.warnings}"
    assert result.safety_flags.get("execution_attempted") is False


def test_run_notification_preview(runner: DemoRunner):
    result = runner.run_scenario("notification_preview")
    assert result.passed, f"notification_preview failed: {result.warnings}"
    assert result.safety_flags.get("os_notification_sent") is False


def test_run_unknown_scenario(runner: DemoRunner):
    result = runner.run_scenario("nonexistent_xyz_9999")
    assert result.passed is False
    assert result.response_type == "error"


# --- run_all ---

def test_run_all_returns_report(runner: DemoRunner):
    report = runner.run_all()
    assert isinstance(report, DemoReport)
    assert report.total_scenarios >= 12
    assert report.passed_scenarios + report.failed_scenarios == report.total_scenarios


def test_run_all_safety_flags_all_false(runner: DemoRunner):
    report = runner.run_all()
    violations = report.safety_summary.get("violations", [])
    assert violations == [], f"Safety violations found: {violations}"


def test_run_all_report_summary(runner: DemoRunner):
    report = runner.run_all()
    assert report.project_name == "ATLAS"
    assert len(report.results) == report.total_scenarios
    assert len(report.recommendations) >= 1


# --- run_category ---

def test_run_category_voice(runner: DemoRunner):
    report = runner.run_category(DemoCategory.VOICE)
    assert isinstance(report, DemoReport)
    for result in report.results:
        assert result.safety_flags.get("microphone_used") is False
        assert result.safety_flags.get("wake_word_used") is False


def test_run_category_safety(runner: DemoRunner):
    report = runner.run_category(DemoCategory.SAFETY)
    assert isinstance(report, DemoReport)
    for result in report.results:
        assert result.safety_flags.get("credential_accessed") is False


# --- validate_safety ---

def test_validate_safety_clean_result(runner: DemoRunner):
    result = runner.run_scenario("chat_chrome_open")
    violations = runner.validate_safety(result)
    assert violations == []


def test_validate_safety_catches_violation():
    dirty = DemoResult(
        scenario_id="fake",
        title="Fake",
        passed=True,
        response_type="answer",
        assistant_message="test",
        command_surface="chat",  # type: ignore[arg-type]
        safety_flags={"execution_attempted": True},
    )
    violations = validate_safety(dirty)
    assert any("execution_attempted" in v for v in violations)
