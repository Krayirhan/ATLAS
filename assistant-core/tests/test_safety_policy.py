from __future__ import annotations

import json
from pathlib import Path

from app.config.models import SafetyPolicyModel
from app.safety.path_guard import is_blocked_path


def _policy(root: Path) -> SafetyPolicyModel:
    raw = json.loads((root / "configs" / "safety-policy.json").read_text(encoding="utf-8"))
    return SafetyPolicyModel.model_validate(raw)


def test_blocked_commands_substrings(isolated_atlas: Path) -> None:
    p = _policy(isolated_atlas)
    from app.safety.command_guard import check_command

    for cmd in (
        "git reset --hard",
        "git clean -fd",
        "git push --force",
        "Remove-Item -Recurse -Force X:\\",
    ):
        r = check_command(cmd, p)
        assert r["blocked"], cmd


def test_blocked_file_patterns(isolated_atlas: Path) -> None:
    p = _policy(isolated_atlas)
    hit, _reason = is_blocked_path(Path(".env"), p)
    assert hit
    hit2, _ = is_blocked_path(Path("id_rsa"), p)
    assert hit2
    hit3, _ = is_blocked_path(Path("leaf.pem"), p)
    assert hit3
