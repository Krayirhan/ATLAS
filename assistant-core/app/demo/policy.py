"""Safety policy validation for Sprint 50 demo results.

Every DemoResult must pass all safety flag checks.
If any forbidden flag is True, the result is marked as a safety failure.
"""

from __future__ import annotations

from app.demo.models import DemoResult
from app.quality.models import SAFETY_INVARIANT_EXPECTED, SAFETY_INVARIANT_FLAGS


def validate_safety(result: DemoResult) -> list[str]:
    """Return a list of safety violation messages. Empty list means all clear."""
    violations: list[str] = []
    flags = result.safety_flags

    missing = [flag for flag in SAFETY_INVARIANT_FLAGS if flag not in flags]
    for flag in missing:
        violations.append(f"SAFETY VIOLATION: {flag} flag is missing")

    for flag, expected in SAFETY_INVARIANT_EXPECTED.items():
        actual = bool(flags.get(flag, False))
        if actual != expected:
            violations.append(f"SAFETY VIOLATION: {flag} must be {expected} but is {actual}")

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
        "execution_boundary": dict(SAFETY_INVARIANT_EXPECTED),
        "note": (
            "All demo scenarios are preview-only. "
            "No real PC, home, calendar, notification, voice, or shell execution occurs."
        ),
    }
