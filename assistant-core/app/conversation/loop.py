import uuid
from typing import Any
from app.actions.intent_router import IntentRouter
from app.actions.types import ActionSource, PermissionStatus
from app.control.pc_adapter import PCControlAdapter
from app.conversation.models import (
    ConversationRequest,
    ConversationResponse,
    ConversationTurn,
    ConversationResponseType
)
from app.conversation.state import get_state_manager
from app.conversation.response_builder import ResponseBuilder

from dataclasses import asdict

class ConversationLoop:
    def __init__(self):
        self.router = IntentRouter()
        self.pc_adapter = PCControlAdapter()
        self.state_manager = get_state_manager()
        self.response_builder = ResponseBuilder()

    def handle(self, request: ConversationRequest) -> ConversationResponse:
        state = self.state_manager.get_state(request.session_id)
        
        # 1. Parse intent and get preview
        preview_result = self.router.preview(request.message, source=request.source)
        intent_obj = preview_result.intent
        intent_res = asdict(intent_obj) if intent_obj else {}
        if intent_obj and hasattr(intent_obj.category, "value"):
            intent_res["category"] = intent_obj.category.value
            
        candidate = preview_result.action_candidate
        decision = preview_result.permission_decision
        
        # 2. Build PC Plan if applicable
        pc_plan = None
        if candidate and decision and decision.status != PermissionStatus.BLOCKED:
            action_type_str = str(candidate.action_type.value) if hasattr(candidate.action_type, "value") else str(candidate.action_type)
            if action_type_str.startswith("pc.") or action_type_str in ("browser.search", "file.search"):
                pc_plan = self.pc_adapter.build_plan(candidate, decision, dry_run=True)
                
        # 3. Build response
        response = self.response_builder.build(
            session_id=request.session_id,
            user_message=request.message,
            intent_result=intent_res,
            action_candidate=candidate,
            permission_decision=decision,
            pc_plan=pc_plan
        )
        
        # 4. Update state
        state.last_intent = intent_res.get("category")
        state.last_action = candidate.action_type if candidate else None
        state.pending_clarification = response.clarification_required
        state.pending_confirmation = response.confirmation_required
        
        turn = ConversationTurn(
            turn_id=str(uuid.uuid4()),
            session_id=request.session_id,
            user_message=request.message,
            assistant_message=response.assistant_message,
            intent_category=state.last_intent or "unknown",
            action_type=state.last_action or "none",
            decision_status=decision.status.value if decision else "none"
        )
        state.turns.append(turn)
        self.state_manager.save_state(state)
        
        return response

    def handle_text(self, message: str, project_name: str = "ATLAS", session_id: str | None = None, source: ActionSource = ActionSource.TEXT) -> ConversationResponse:
        session_id = session_id or str(uuid.uuid4())
        req = ConversationRequest(
            project_name=project_name,
            message=message,
            source=source,
            session_id=session_id
        )
        return self.handle(req)

    def reset_session(self, session_id: str):
        return self.state_manager.reset_session(session_id)

    def get_state(self, session_id: str):
        return self.state_manager.get_state(session_id)
