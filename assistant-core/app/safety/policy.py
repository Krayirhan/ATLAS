"""Load safety-policy.json."""

from __future__ import annotations

from app.config.loader import load_safety_policy
from app.config.models import SafetyPolicyModel
from app.paths import get_configs_dir


def get_safety_policy() -> SafetyPolicyModel:
    return load_safety_policy(get_configs_dir())
