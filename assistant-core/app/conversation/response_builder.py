from typing import Any

from app.actions.models import ActionCandidate, PermissionDecision
from app.actions.risk import RiskLevel
from app.actions.types import PermissionStatus
from app.control.models import PCControlPlan
from app.conversation.models import ConversationResponse, ConversationResponseType


class ResponseBuilder:
    @staticmethod
    def build(
        session_id: str,
        user_message: str,
        intent_result: dict[str, Any],
        action_candidate: ActionCandidate | None = None,
        permission_decision: PermissionDecision | None = None,
        pc_plan: PCControlPlan | None = None,
    ) -> ConversationResponse:
        category = intent_result.get("category", "unknown")

        if category in {"conversation.question", "conversation.status"} and not action_candidate:
            return ConversationResponse(
                session_id=session_id,
                user_message=user_message,
                assistant_message="Bu bir bilgi veya durum istegi olarak algilandi. Gercek islem yapilmadi.",
                response_type=ConversationResponseType.ANSWER,
                intent=intent_result,
            )

        if intent_result.get("requires_clarification", False) or category == "unknown":
            return ConversationResponse(
                session_id=session_id,
                user_message=user_message,
                assistant_message="Belirsiz hedef. Hangi hedefi kastettigini belirtmelisin. Gercek islem yapilmadi.",
                response_type=ConversationResponseType.CLARIFICATION,
                intent=intent_result,
                clarification_required=True,
            )

        if category == "blocked" or (permission_decision and permission_decision.status == PermissionStatus.BLOCKED):
            return ConversationResponse(
                session_id=session_id,
                user_message=user_message,
                assistant_message=(
                    "Bu istek guvenlik politikasi nedeniyle engellendi. "
                    "Gizli bilgi veya credential okuma aksiyonlari calistirilamaz. Gercek islem yapilmadi."
                ),
                response_type=ConversationResponseType.BLOCKED,
                intent=intent_result,
                action_candidate=action_candidate,
                permission_decision=permission_decision,
                blocked=True,
            )

        if not action_candidate or not permission_decision:
            return ConversationResponse(
                session_id=session_id,
                user_message=user_message,
                assistant_message="Bu istegi guvenli sekilde siniflandiramadim. Gercek islem yapilmadi.",
                response_type=ConversationResponseType.UNSUPPORTED,
                intent=intent_result,
            )

        if permission_decision.status == PermissionStatus.CONFIRMATION_REQUIRED:
            msg = (
                f"Bunu {action_candidate.user_goal} istegi olarak anladim. "
                "Bu onizleme akisi durum degisikligi yapabilecek bir istek; onay gerekiyor. Gercek islem yapilmadi."
            )
            if permission_decision.risk_level.value == RiskLevel.HIGH.value:
                msg = (
                    f"Bunu {action_candidate.user_goal} istegi olarak anladim. "
                    "Bu yuksek riskli bir islem. Acik onay olmadan calistirilamaz ve gercek islem yapilmadi."
                )
            elif str(action_candidate.action_type).startswith("device.") or getattr(action_candidate.action_type, "value", "").startswith("device."):
                msg = (
                    f"Bunu {action_candidate.user_goal} istegi olarak anladim. "
                    "Bu fiziksel cihaz durumunu degistirebilecek bir onizlemedir; onay gerekiyor. "
                    "Ev kontrol adapteri henuz aktif degil; su an yalnizca aksiyon onizlemesi yapilabilir ve gercek islem yapilmadi."
                )
            return ConversationResponse(
                session_id=session_id,
                user_message=user_message,
                assistant_message=msg,
                response_type=ConversationResponseType.CONFIRMATION_REQUIRED,
                intent=intent_result,
                action_candidate=action_candidate,
                permission_decision=permission_decision,
                pc_plan=pc_plan,
                confirmation_required=True,
            )

        if pc_plan and pc_plan.dry_run:
            return ConversationResponse(
                session_id=session_id,
                user_message=user_message,
                assistant_message=(
                    f"{action_candidate.user_goal} istegini {action_candidate.action_type} olarak anladim. "
                    "Bu dusuk riskli bir PC onizlemesi. Su an yalnizca guvenli onizleme modundayim; gercek uygulama acma yapilmadi."
                ),
                response_type=ConversationResponseType.ACTION_PREVIEW,
                intent=intent_result,
                action_candidate=action_candidate,
                permission_decision=permission_decision,
                pc_plan=pc_plan,
            )

        return ConversationResponse(
            session_id=session_id,
            user_message=user_message,
            assistant_message=(
                f"{action_candidate.user_goal} istegini anladim. "
                "Bu akis yalnizca onizleme veya confirmation seviyesindedir; gercek islem yapilmadi."
            ),
            response_type=ConversationResponseType.ACTION_PREVIEW,
            intent=intent_result,
            action_candidate=action_candidate,
            permission_decision=permission_decision,
            pc_plan=pc_plan,
        )
