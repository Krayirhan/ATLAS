"""Permission decision engine for ATLAS personal actions.

PermissionManager never executes actions and never calls adapters.
"""

from __future__ import annotations

from app.actions.audit import build_permission_audit_metadata, result_audit_metadata
from app.actions.models import ActionCandidate, ActionPreview, ActionResult, PermissionDecision
from app.actions.preview import build_action_preview
from app.actions.risk import RiskLevel
from app.actions.types import ActionSource, ActionStatus, IntentCategory, PermissionStatus


class PermissionManager:
    """Create previews and permission decisions for personal action candidates."""

    def __init__(self, *, voice_confidence_threshold: float = 0.70) -> None:
        self.voice_confidence_threshold = voice_confidence_threshold

    def build_preview(self, action: ActionCandidate) -> ActionPreview:
        return build_action_preview(action)

    def decide(self, action: ActionCandidate) -> PermissionDecision:
        preview = self.build_preview(action)

        if action.risk_level is RiskLevel.BLOCKED:
            return self.block(action, action.blocked_reason or "Action ATLAS policy tarafindan engellidir.", preview=preview)
        if action.intent_category in {IntentCategory.AMBIGUOUS, IntentCategory.UNKNOWN}:
            return self._clarification_decision(
                action,
                preview=preview,
                reason="Intent net degil; action uretilmeden once kullanicidan netlestirme istenmeli.",
            )
        if not action.target.strip():
            return self._clarification_decision(
                action,
                preview=preview,
                reason="Action hedefi eksik; execution veya adapter akisina gecilemez.",
            )
        if action.source is ActionSource.VOICE and self._voice_confidence(action) < self.voice_confidence_threshold:
            return self._clarification_decision(
                action,
                preview=preview,
                reason="Sesli komut confidence dusuk; action oncesi tekrar netlestirme gerekir.",
            )
        if action.risk_level is RiskLevel.SAFE_READONLY:
            return self._decision(
                action,
                status=PermissionStatus.SAFE_READONLY,
                preview=preview,
                allowed_to_execute=True,
                requires_confirmation=False,
                requires_clarification=False,
                blocked=False,
                reason="Safe read-only action; state degistirmez.",
                confirmation_prompt="",
                warnings=preview.warnings,
                next_step="Read-only result akisi veya onizleme uretilebilir; Sprint 38 execution yapmaz.",
            )
        if action.risk_level is RiskLevel.LOW:
            return self._decision(
                action,
                status=PermissionStatus.PREVIEW_ALLOWED,
                preview=preview,
                allowed_to_execute=True,
                requires_confirmation=False,
                requires_clarification=False,
                blocked=False,
                reason="Low risk action preview allowed.",
                confirmation_prompt="",
                warnings=preview.warnings,
                next_step="Gelecek adapter yalnizca permission gate sonrasi kullanilabilir; Sprint 38 execution yapmaz.",
            )
        if action.risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH}:
            prompt = self._confirmation_prompt(action)
            warnings = list(preview.warnings)
            if action.risk_level is RiskLevel.HIGH and not warnings:
                warnings.append("Yuksek riskli action icin guclu uyari gerekir.")
            return self._decision(
                action,
                status=PermissionStatus.CONFIRMATION_REQUIRED,
                preview=preview,
                allowed_to_execute=False,
                requires_confirmation=True,
                requires_clarification=False,
                blocked=False,
                reason="Medium/high risk action explicit confirmation gerektirir.",
                confirmation_prompt=prompt,
                warnings=warnings,
                next_step="Kullanici acik onay verirse ActionResult approved uretilir; adapter cagrilmaz.",
            )
        return self._decision(
            action,
            status=PermissionStatus.UNKNOWN,
            preview=preview,
            allowed_to_execute=False,
            requires_confirmation=False,
            requires_clarification=True,
            blocked=False,
            reason="Risk seviyesi permission engine tarafindan yorumlanamadi.",
            confirmation_prompt="",
            warnings=["Unknown permission state."],
            next_step="Action schema ve risk siniflandirmasini duzeltin.",
        )

    def confirm(self, decision: PermissionDecision, confirmed: bool) -> ActionResult:
        if not confirmed:
            return self.deny(decision)
        if decision.status is PermissionStatus.BLOCKED:
            return self._result(decision, status=ActionStatus.BLOCKED, message="Blocked action onayla calistirilamaz.")
        if decision.status is PermissionStatus.CLARIFICATION_REQUIRED:
            return self._result(decision, status=ActionStatus.SKIPPED, message="Clarification gerekli; action onaylanmadi.")
        if decision.status is not PermissionStatus.CONFIRMATION_REQUIRED:
            return self._result(decision, status=ActionStatus.APPROVED, message="Permission karari onaylandi; Sprint 38 adapter cagirmaz.")
        return self._result(decision, status=ActionStatus.APPROVED, message="Kullanici onayi alindi; Sprint 38 execution yapmaz.")

    def deny(self, decision: PermissionDecision) -> ActionResult:
        return self._result(decision, status=ActionStatus.DENIED, message="Kullanici action istegini reddetti.")

    def cancel(self, decision: PermissionDecision) -> ActionResult:
        return self._result(decision, status=ActionStatus.CANCELLED, message="Permission akisi iptal edildi.")

    def block(self, action: ActionCandidate, reason: str, *, preview: ActionPreview | None = None) -> PermissionDecision:
        preview = preview or self.build_preview(action)
        return self._decision(
            action,
            status=PermissionStatus.BLOCKED,
            preview=preview,
            allowed_to_execute=False,
            requires_confirmation=False,
            requires_clarification=False,
            blocked=True,
            reason=reason,
            confirmation_prompt=self._blocked_prompt(reason),
            warnings=[reason],
            next_step="Guvenli alternatif olarak read-only preview veya clarification oner.",
        )

    def _clarification_decision(self, action: ActionCandidate, *, preview: ActionPreview, reason: str) -> PermissionDecision:
        return self._decision(
            action,
            status=PermissionStatus.CLARIFICATION_REQUIRED,
            preview=preview,
            allowed_to_execute=False,
            requires_confirmation=False,
            requires_clarification=True,
            blocked=False,
            reason=reason,
            confirmation_prompt=self._clarification_prompt(action),
            warnings=preview.warnings,
            next_step="Kullanicidan hedef, oda, cihaz, zaman veya parametre netlestirmesi iste.",
        )

    def _decision(
        self,
        action: ActionCandidate,
        *,
        status: PermissionStatus,
        preview: ActionPreview,
        allowed_to_execute: bool,
        requires_confirmation: bool,
        requires_clarification: bool,
        blocked: bool,
        reason: str,
        confirmation_prompt: str,
        warnings: list[str],
        next_step: str,
    ) -> PermissionDecision:
        audit_metadata = build_permission_audit_metadata(
            action,
            decision_status=status,
            requires_confirmation=requires_confirmation,
            blocked=blocked,
        )
        return PermissionDecision(
            action_id=action.action_id,
            status=status,
            risk_level=action.risk_level,
            allowed_to_execute=allowed_to_execute,
            requires_confirmation=requires_confirmation,
            requires_clarification=requires_clarification,
            blocked=blocked,
            reason=reason,
            confirmation_prompt=confirmation_prompt,
            warnings=warnings,
            audit_metadata=audit_metadata,
            next_step=next_step,
            preview=preview,
        )

    def _result(self, decision: PermissionDecision, *, status: ActionStatus, message: str) -> ActionResult:
        return ActionResult(
            action_id=decision.action_id,
            status=status,
            executed=False,
            dry_run=True,
            message=message,
            audit_metadata=result_audit_metadata(decision.audit_metadata, result_status=status.value),
        )

    def _confirmation_prompt(self, action: ActionCandidate) -> str:
        base = f"{action.target} hedefinde {action.action_type.value} yapmami onayliyor musun?"
        if action.risk_level is RiskLevel.HIGH:
            base = (
                f"Yuksek riskli islem: {action.target} hedefinde {action.action_type.value} yapmak uzeresin. "
                "Acik calismalar, gizlilik veya fiziksel ortam etkilenebilir. Devam etmemi acikca onayliyor musun?"
            )
        if action.source is ActionSource.VOICE:
            if action.risk_level is RiskLevel.HIGH:
                return (
                    "Sesli komut olarak algilandi. Yuksek riskli voice isteginde kisa bir 'evet' yeterli degildir. "
                    "Hedefi ve islemi acikca tekrar eden net bir onay gerekir. "
                    f"{base}"
                )
            return (
                "Sesli komut olarak algilandi. Bu voice istegi icin acik onay gerekiyor; "
                "kisa bir 'evet' yerine hedefi ve islemi belirten net bir onay kullan. "
                f"{base}"
            )
        return base

    def _blocked_prompt(self, reason: str) -> str:
        return f"Bu islem guvenlik politikasi nedeniyle calistirilamaz: {reason}"

    def _clarification_prompt(self, action: ActionCandidate) -> str:
        if action.intent_category in {IntentCategory.AMBIGUOUS, IntentCategory.UNKNOWN}:
            return "Komutu netlestirmem gerekiyor. Hedef, oda, cihaz veya islem adini belirt."
        if not action.target.strip():
            return "Hedef eksik. Hangi hedef icin islem yapmami istiyorsun?"
        return "Bu action icin ek bilgi gerekiyor."

    def _voice_confidence(self, action: ActionCandidate) -> float:
        value = action.audit_metadata.get("confidence", 1.0)
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
