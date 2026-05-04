"""Path checks against safety policy."""

from __future__ import annotations

from pathlib import Path

from app.config.models import SafetyPolicyModel


def path_under_any_root(path: Path, roots: list[str]) -> bool:
    p = path.resolve()
    for r in roots:
        try:
            p.relative_to(Path(r).resolve())
            return True
        except ValueError:
            continue
    return False


def is_blocked_path(path: Path, policy: SafetyPolicyModel) -> tuple[bool, str | None]:
    p = str(path.resolve())
    low = p.lower()
    for blocked in policy.blocked_paths:
        b = blocked.lower().rstrip("\\/")
        if b and b in low:
            return True, f"matches blocked_paths entry: {blocked}"
    for pattern in policy.blocked_file_patterns:
        if _matches_file_pattern(path.name, pattern):
            return True, f"matches blocked_file_patterns: {pattern}"
    return False, None


def _matches_file_pattern(name: str, pattern: str) -> bool:
    if pattern.startswith("*."):
        return name.lower().endswith(pattern[1:].lower())
    return name.lower() == pattern.lower()


def is_allowed_workspace_path(path: Path, policy: SafetyPolicyModel) -> bool:
    return path_under_any_root(path, policy.allowed_workspace_roots)
