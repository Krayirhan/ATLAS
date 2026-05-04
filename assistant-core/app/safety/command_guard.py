"""Command string checks: blocked tokens and approval-required hints."""

from __future__ import annotations

import re

from app.config.models import SafetyPolicyModel


def _norm(cmd: str) -> str:
    return re.sub(r"\s+", " ", cmd.strip()).lower()


def check_command(cmd: str, policy: SafetyPolicyModel) -> dict:
    """
    Returns dict: allowed (bool), blocked (bool), approval_required (bool), reasons (list).
    """
    reasons: list[str] = []
    n = _norm(cmd)
    blocked_hit = False
    for token in policy.blocked_commands:
        t = token.strip().lower()
        if t and t in n:
            blocked_hit = True
            reasons.append(f"blocked_commands contains: {token}")
    approval = False
    for token in policy.approval_required_commands:
        t = token.strip().lower()
        if t and t in n:
            approval = True
            reasons.append(f"approval_required_commands contains: {token}")
    allowed = not blocked_hit
    return {
        "allowed": allowed,
        "blocked": blocked_hit,
        "approval_required": approval,
        "reasons": reasons,
    }
