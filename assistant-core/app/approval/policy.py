"""Helpers for approval-only policy classification."""

from __future__ import annotations

from app.config.models import SafetyPolicyModel
from app.safety.policy import get_safety_policy

SAFE_READONLY_PREFIXES = (
    "python -m app.cli ai memory",
    "python -m app.cli ai ask-agent",
    "python -m app.cli ai plan",
    "python -m app.cli ai review",
    "python -m app.cli logs list",
    "python -m app.cli logs show",
    "python -m app.cli logs project",
    "python -m app.cli project list",
    "python -m app.cli project show",
    "python -m app.cli project validate",
)

PREVIEW_ALLOWED_PREFIXES = (
    "python -m pytest -q",
    "python -m app.cli doctor --full",
    "python -m app.cli config validate",
    "python -m app.cli report list",
    "python -m app.cli report latest",
    "python -m app.cli context show-plan",
)

APPROVAL_REQUIRED_EXTRAS = (
    "generated mcp install",
    "mcp install",
)

BLOCKED_PATH_TOKENS = (
    r"d:\atlas",
    r"c:\users",
    "browser profile",
    "appdata",
)

BLOCKED_FILE_TOKENS = (
    ".env",
    ".pem",
    ".key",
    ".keystore",
    ".jks",
    "id_rsa",
    "id_ed25519",
    "keystore",
)


def load_approval_policy() -> SafetyPolicyModel:
    return get_safety_policy()
