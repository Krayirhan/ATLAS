"""Preview builder for ATLAS personal action candidates.

The builder creates ActionPreview objects only. It does not execute actions.
"""

from __future__ import annotations

from app.actions.models import ActionCandidate, ActionPreview
from app.actions.risk import RiskLevel
from app.actions.types import ActionSource, IntentCategory


def build_action_preview(action: ActionCandidate) -> ActionPreview:
    """Create a policy preview for an action candidate."""

    if action.intent_category in {IntentCategory.AMBIGUOUS, IntentCategory.UNKNOWN}:
        return _clarification_preview(action, "Komut yeterince net degil; hedef veya islem bilgisi eksik.")
    if not action.target.strip():
        return _clarification_preview(action, "Hedef eksik; islem yapmadan once hedef netlesmeli.")
    if action.risk_level is RiskLevel.BLOCKED:
        reason = action.blocked_reason or "Bu action ATLAS permission policy tarafindan engellidir."
        return ActionPreview(
            action_id=action.action_id,
            summary=f"Engelli action: {action.action_type.value}",
            target=action.target,
            parameters_preview=dict(action.parameters),
            risk_level=RiskLevel.BLOCKED,
            will_change_state=True,
            requires_confirmation=False,
            reversible=False,
            estimated_effect="Islem calistirilmaz.",
            warnings=[reason],
            safe_to_execute=False,
            blocked_reason=reason,
        )

    warnings = _warnings_for(action)
    return ActionPreview(
        action_id=action.action_id,
        summary=f"{action.action_type.value} icin onizleme hazirlandi.",
        target=action.target,
        parameters_preview=dict(action.parameters),
        risk_level=action.risk_level,
        will_change_state=_will_change_state(action),
        requires_confirmation=action.requires_confirmation,
        reversible=action.reversible,
        estimated_effect=action.expected_result,
        warnings=warnings,
        safe_to_execute=action.risk_level in {RiskLevel.SAFE_READONLY, RiskLevel.LOW},
        blocked_reason="",
    )


def _clarification_preview(action: ActionCandidate, reason: str) -> ActionPreview:
    return ActionPreview(
        action_id=action.action_id,
        summary="Clarification required before action preview.",
        target=action.target or "<missing>",
        parameters_preview=dict(action.parameters),
        risk_level=action.risk_level,
        will_change_state=False,
        requires_confirmation=False,
        reversible=action.reversible,
        estimated_effect=reason,
        warnings=[reason],
        safe_to_execute=False,
        blocked_reason="",
        requires_clarification=True,
    )


def _will_change_state(action: ActionCandidate) -> bool:
    if action.risk_level is RiskLevel.SAFE_READONLY:
        return False
    if action.risk_level is RiskLevel.LOW:
        return action.source is not ActionSource.UNKNOWN
    return action.risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.BLOCKED}


def _warnings_for(action: ActionCandidate) -> list[str]:
    warnings: list[str] = []
    if action.risk_level is RiskLevel.HIGH:
        warnings.append("Yuksek riskli action: calisma, gizlilik veya fiziksel ortam etkilenebilir.")
    if action.source is ActionSource.VOICE and action.risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH}:
        warnings.append("Sesli komut kaynagi: hedef ve islem tekrar dogrulanmali.")
    return warnings
