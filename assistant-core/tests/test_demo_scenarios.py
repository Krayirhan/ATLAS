"""Tests for built-in demo scenarios (Sprint 50)."""

import pytest

from app.demo.models import CommandSurface, DemoCategory, DemoScenario
from app.demo.scenarios import BUILTIN_SCENARIOS, get_scenario, get_scenarios_by_category


def test_minimum_scenario_count():
    assert len(BUILTIN_SCENARIOS) >= 12


def test_scenario_ids_are_unique():
    ids = [s.scenario_id for s in BUILTIN_SCENARIOS]
    assert len(ids) == len(set(ids)), "Duplicate scenario IDs found"


def test_all_scenarios_have_expected_safety_flags():
    required_flags = {
        "execution_attempted",
        "physical_device_touched",
        "network_used",
        "microphone_used",
        "wake_word_used",
        "audio_retained",
        "external_calendar_used",
        "os_notification_sent",
        "credential_accessed",
        "shell_used",
    }
    for scenario in BUILTIN_SCENARIOS:
        missing = required_flags - set(scenario.expected_safety_flags.keys())
        assert not missing, f"Scenario {scenario.scenario_id} missing flags: {missing}"


def test_all_scenarios_have_titles():
    for scenario in BUILTIN_SCENARIOS:
        assert scenario.title, f"Scenario {scenario.scenario_id} has empty title"


def test_all_scenarios_have_input_text():
    for scenario in BUILTIN_SCENARIOS:
        assert scenario.input_text, f"Scenario {scenario.scenario_id} has empty input_text"


def test_all_expected_safety_flags_are_false():
    """All expected safety flags in built-in scenarios must be False (safe)."""
    for scenario in BUILTIN_SCENARIOS:
        for flag, value in scenario.expected_safety_flags.items():
            assert value is False, (
                f"Scenario {scenario.scenario_id}: expected_safety_flags[{flag}] "
                f"must be False but is {value}"
            )


def test_required_scenarios_present():
    required_ids = {
        "chat_chrome_open",
        "ambiguous_light",
        "blocked_secret",
        "voice_home_preview",
        "reminder_create",
        "calendar_draft",
    }
    existing_ids = {s.scenario_id for s in BUILTIN_SCENARIOS}
    missing = required_ids - existing_ids
    assert not missing, f"Missing required scenarios: {missing}"


def test_get_scenario_found():
    scenario = get_scenario("chat_chrome_open")
    assert scenario is not None
    assert scenario.scenario_id == "chat_chrome_open"


def test_get_scenario_not_found():
    scenario = get_scenario("nonexistent_xyz")
    assert scenario is None


def test_get_scenarios_by_category():
    voice_scenarios = get_scenarios_by_category(DemoCategory.VOICE)
    assert all(s.category == DemoCategory.VOICE for s in voice_scenarios)


def test_safety_category_present():
    safety_scenarios = get_scenarios_by_category(DemoCategory.SAFETY)
    assert len(safety_scenarios) >= 1


def test_blocked_scenarios_have_correct_expected_response():
    blocked = [s for s in BUILTIN_SCENARIOS if "blocked" in s.scenario_id]
    for s in blocked:
        assert "blocked" in s.expected_response_type


def test_voice_scenario_flags():
    voice = get_scenario("voice_home_preview")
    assert voice is not None
    assert voice.expected_safety_flags["microphone_used"] is False
    assert voice.expected_safety_flags["wake_word_used"] is False
    assert voice.expected_safety_flags["audio_retained"] is False


def test_calendar_draft_scenario():
    s = get_scenario("calendar_draft")
    assert s is not None
    assert s.command_surface == CommandSurface.CALENDAR
    assert s.expected_safety_flags["external_calendar_used"] is False


def test_notification_preview_scenario():
    s = get_scenario("notification_preview")
    assert s is not None
    assert s.expected_safety_flags["os_notification_sent"] is False
