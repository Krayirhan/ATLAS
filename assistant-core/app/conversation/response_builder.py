from typing import Any
from app.actions.models import ActionCandidate, PermissionDecision
from app.actions.types import PermissionStatus
from app.actions.risk import RiskLevel
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
        pc_plan: PCControlPlan | None = None
    ) -> ConversationResponse:
        
        category = intent_result.get("category", "unknown")
        
        if category in {"conversation.question", "conversation.status"} and not action_candidate:
            return ConversationResponse(
                session_id=session_id,
                user_message=user_message,
                assistant_message="Bu bir bilgi/soru isteği olarak algılandı. Şu an action çalıştırılmadı.",
                response_type=ConversationResponseType.ANSWER,
                intent=intent_result,
            )
            
        if intent_result.get("requires_clarification", False) or category == "unknown":
            return ConversationResponse(
                session_id=session_id,
                user_message=user_message,
                assistant_message="Hangi hedefi kastettiğini belirtmelisin.",
                response_type=ConversationResponseType.CLARIFICATION,
                intent=intent_result,
                clarification_required=True,
            )
            
        if category == "blocked" or (permission_decision and permission_decision.status == PermissionStatus.BLOCKED):
            reason = permission_decision.reason if permission_decision else "Bu istek güvenlik politikası nedeniyle engellendi."
            return ConversationResponse(
                session_id=session_id,
                user_message=user_message,
                assistant_message="Bu istek güvenlik politikası nedeniyle engellendi. Gizli bilgi veya credential okuma aksiyonları çalıştırılamaz.",
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
                assistant_message="Bu isteği güvenli şekilde sınıflandıramadım.",
                response_type=ConversationResponseType.UNSUPPORTED,
                intent=intent_result,
            )
            
        if permission_decision.status == PermissionStatus.CONFIRMATION_REQUIRED:
            msg = f"Bunu {action_candidate.user_goal} isteği olarak anladım. Bu işlem durum değişikliği yapabilir ve onay gerektirir."
            if permission_decision.risk_level.value == RiskLevel.HIGH.value:
                msg = f"Bunu {action_candidate.user_goal} isteği olarak anladım. Bu yüksek riskli işlem. Açık onay olmadan çalıştırılamaz."
            elif str(action_candidate.action_type).startswith("device.") or getattr(action_candidate.action_type, "value", "").startswith("device."):
                msg = f"Bunu {action_candidate.user_goal} isteği olarak anladım. Bu fiziksel cihaz durumunu değiştireceği için onay gerektirir. Ev kontrol adapterı henüz aktif değil; şu an yalnızca aksiyon önizlemesi yapılabilir."
                
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
                assistant_message=f"{action_candidate.user_goal} isteğini {action_candidate.action_type} olarak anladım. Bu düşük riskli bir PC aksiyonu. Şu an yalnızca güvenli önizleme modundayım; gerçek uygulama açma yapılmadı.",
                response_type=ConversationResponseType.ACTION_PREVIEW,
                intent=intent_result,
                action_candidate=action_candidate,
                permission_decision=permission_decision,
                pc_plan=pc_plan,
            )
            
        return ConversationResponse(
            session_id=session_id,
            user_message=user_message,
            assistant_message=f"{action_candidate.user_goal} isteği olarak anladım. İşlem yapıldı (MVP gereği mock).",
            response_type=ConversationResponseType.ACTION_PREVIEW,
            intent=intent_result,
            action_candidate=action_candidate,
            permission_decision=permission_decision,
            pc_plan=pc_plan,
        )
