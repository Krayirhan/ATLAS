"""Supported project types (Sprint 21 multi-project rollout)."""

from __future__ import annotations

# Sprint 21 canonical types + internal ATLAS tooling type used in this repo.
ALLOWED_PROJECT_TYPES = frozenset(
    {
        "android-compose-room",
        "android-compose-notes",
        "mlops-python",
        "spring-boot",
        "unity-game",
        "plain-java",
        "python-cli",
    }
)


def validate_project_type(project_type: str) -> str:
    t = (project_type or "").strip()
    if not t:
        raise ValueError("project type must be non-empty")
    if t not in ALLOWED_PROJECT_TYPES:
        allowed = ", ".join(sorted(ALLOWED_PROJECT_TYPES))
        raise ValueError(f"Unsupported project type: {t!r}. Allowed: {allowed}")
    return t
