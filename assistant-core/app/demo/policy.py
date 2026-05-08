"""Safety policy validation for Sprint 50 demo results.

Every DemoResult must pass all safety flag checks.
If any forbidden flag is True, the result is marked as a safety failure.
"""

from __future__ import annotations

from app.demo.models import DemoResult

# Flags that must be False in every demo result.
_FORBIDDEN_TRUE_FLAGS: tuple[str, ...] = (
    "execution_attempted",
    "physical_device_touched",
    "network_used",
    "wake_word_used",
    "audio_retained",
    "external_calendar_used",
    "os_notification_sent",
    "credential_accessed",
    "shell_used",
)

# microphone_used is allowed only for mock; if the value is True and not tagged mock,
# it is a violation. For the demo runner we always use mock, so we enforce False.
_MICROPHONE_FLAG = "microphone_used"


def validate_safety(result: DemoResult) -> list[str]:
    """Return a list of safety violation messages. Empty list means all clear."""
    violations: list[str] = []
    flags = result.safety_flags

    for flag in _FORBIDDEN_TRUE_FLAGS:
        if flags.get(flag, False) is True:
            violations.append(f"SAFETY VIOLATION: {flag} must be False but is True")

    if flags.get(_MICROPHONE_FLAG, False) is True:
        violations.append(
            "SAFETY VIOLATION: microphone_used must be False "
            "(only mock transcript allowed in demo)"
        )

    return violations


def is_safe(result: DemoResult) -> bool:
    return len(validate_safety(result)) == 0


def build_safety_summary(results: list[DemoResult]) -> dict:
    """Build an aggregate safety summary across all results."""
    all_violations: list[dict] = []
    for result in results:
        for v in validate_safety(result):
            all_violations.append({"scenario_id": result.scenario_id, "violation": v})

    return {
        "total_scenarios": len(results),
        "safe_scenarios": sum(1 for r in results if is_safe(r)),
        "unsafe_scenarios": sum(1 for r in results if not is_safe(r)),
        "violations": all_violations,
        "execution_boundary": {
            "execution_attempted": False,
            "physical_device_touched": False,
            "network_used": False,
            "microphone_used": False,
            "wake_word_used": False,
            "audio_retained": False,
            "external_calendar_used": False,
            "os_notification_sent": False,
            "credential_accessed": False,
            "shell_used": False,
        },
        "note": (
            "All demo scenarios are preview-only. "
            "No real PC, home, calendar, notification, voice, or shell execution occurs."
        ),
    }
