import uuid
from typing import Any
from app.actions.intent_router import IntentRouter
from app.actions.types import ActionSource, PermissionStatus
from app.control.pc_adapter import PCControlAdapter
from app.devices.planner import DeviceActionPlanner
from app.devices.models import DeviceRegistryStatus
from app.conversation.models import (
    ConversationRequest,
    ConversationResponse,
    ConversationTurn,
    ConversationResponseType
)
from app.conversation.state import get_state_manager
from app.conversation.response_builder import ResponseBuilder

from dataclasses import asdict

from app.personal_memory.service import PersonalMemoryService
from app.personal_memory.intents import MemoryIntentParser
from app.personal_memory.models import MemoryOperation, MemoryOperationStatus
from app.personal_assistant.models import (
    CalendarOperation,
    CalendarOperationResult,
    CalendarStatus,
    ReminderOperation,
    ReminderOperationResult,
    ReminderResultStatus,
)
from app.personal_assistant.service import PersonalAssistantService

class ConversationLoop:
    def __init__(self):
        self.router = IntentRouter()
        self.pc_adapter = PCControlAdapter()
        self.device_planner = DeviceActionPlanner(router=self.router)
        self.state_manager = get_state_manager()
        self.response_builder = ResponseBuilder()
        self.personal_assistant = PersonalAssistantService()

    def handle(self, request: ConversationRequest) -> ConversationResponse:
        state = self.state_manager.get_state(request.session_id)
        
        # 0. Check memory intent first
        op, _, _ = MemoryIntentParser.parse(request.message)
        if op != MemoryOperation.UNKNOWN:
            mem_service = PersonalMemoryService()
            mem_res = mem_service.handle_text(request.message)
            
            resp_type = ConversationResponseType.ANSWER
            if mem_res.status == MemoryOperationStatus.BLOCKED:
                resp_type = ConversationResponseType.BLOCKED
                
            response = ConversationResponse(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=mem_res.message,
                response_type=resp_type,
                blocked=mem_res.status == MemoryOperationStatus.BLOCKED
            )
            
            # Update state for memory operation
            state.last_intent = "memory." + op.value
            state.last_action = "none"
            state.turns.append(ConversationTurn(
                turn_id=str(uuid.uuid4()),
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=response.assistant_message,
                intent_category=state.last_intent,
                action_type=state.last_action,
                decision_status="none"
            ))
            self.state_manager.save_state(state)
            return response

        personal_result = self.personal_assistant.handle_text(request.message, source=request.source)
        if personal_result is not None:
            response = self._build_personal_assistant_response(request, personal_result)
            state.last_intent = response.intent.get("category") if response.intent else "personal_assistant"
            state.last_action = response.metadata.get("action_type")
            state.pending_clarification = response.clarification_required
            state.pending_confirmation = response.confirmation_required
            state.turns.append(ConversationTurn(
                turn_id=str(uuid.uuid4()),
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=response.assistant_message,
                intent_category=state.last_intent or "personal_assistant",
                action_type=state.last_action or "none",
                decision_status=response.metadata.get("decision_status", "none"),
            ))
            self.state_manager.save_state(state)
            return response
            
        # 0.5 Check routine intent
        from app.routines.service import RoutineService
        routine_service = RoutineService()
        routine_name, operation = routine_service.parse_routine_request(request.message)
        if operation != "unknown":
            routine_result = routine_service.handle_text(request.message)
            res_message = routine_service.format_response(routine_result)
            resp_type = ConversationResponseType.ANSWER
            
            if "engellendi" in res_message.lower():
                resp_type = ConversationResponseType.BLOCKED
            elif "onay bekliyor" in res_message.lower():
                resp_type = ConversationResponseType.CONFIRMATION_REQUIRED
            elif "güvenli" in res_message.lower():
                resp_type = ConversationResponseType.ACTION_PREVIEW
                
            response = ConversationResponse(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=res_message,
                response_type=resp_type,
                blocked=resp_type == ConversationResponseType.BLOCKED,
                confirmation_required=resp_type == ConversationResponseType.CONFIRMATION_REQUIRED
            )
            
            state.last_intent = "routine." + operation
            state.last_action = "none"
            state.pending_confirmation = response.confirmation_required
            state.turns.append(ConversationTurn(
                turn_id=str(uuid.uuid4()),
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=response.assistant_message,
                intent_category=state.last_intent,
                action_type=state.last_action,
                decision_status="none"
            ))
            self.state_manager.save_state(state)
            return response
        
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

        device_response = None
        if self._is_device_like(request.message, candidate):
            device_response = self._build_device_response(
                request=request,
                intent_res=intent_res,
                action_candidate=candidate,
                permission_decision=decision,
            )
                
        # 3. Build response
        response = device_response or self.response_builder.build(
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

    def _build_personal_assistant_response(self, request: ConversationRequest, result: ReminderOperationResult | CalendarOperationResult) -> ConversationResponse:
        if isinstance(result, ReminderOperationResult):
            message = self.personal_assistant.reminder_service.format_result(result)
            reminder = result.reminder
            action_type = {
                ReminderOperation.CREATE: "reminder.create",
                ReminderOperation.LIST: "reminder.list",
                ReminderOperation.CANCEL: "reminder.cancel",
                ReminderOperation.PREVIEW: "reminder.preview",
            }.get(result.operation, "reminder.unknown")
            risk_level = "safe_readonly"
            response_type = ConversationResponseType.ANSWER
            confirmation_required = False
            blocked = False
            decision_status = "listed"
            if result.status is ReminderResultStatus.PENDING_CONFIRMATION:
                risk_level = "medium"
                response_type = ConversationResponseType.CONFIRMATION_REQUIRED
                confirmation_required = True
                decision_status = "confirmation_required"
            elif result.status is ReminderResultStatus.BLOCKED:
                risk_level = "blocked"
                response_type = ConversationResponseType.BLOCKED
                blocked = True
                decision_status = "blocked"
            elif result.status is ReminderResultStatus.PREVIEW:
                response_type = ConversationResponseType.ACTION_PREVIEW
                decision_status = "preview"
            intent = {
                "category": action_type,
                "target": reminder.title if reminder is not None else "",
                "requires_clarification": False,
            }
            metadata = {
                "source": request.source.value,
                "action_type": action_type,
                "risk_level": risk_level,
                "target": reminder.title if reminder is not None else "",
                "decision_status": decision_status,
                "personal_assistant": {
                    "scope": "reminder",
                    "operation": result.operation.value,
                    "status": result.status.value,
                    "target": reminder.title if reminder is not None else "",
                    "risk_level": risk_level,
                    "panel_title": "Reminder preview" if result.operation is ReminderOperation.CREATE else "Reminder local state",
                    "panel_summary": message,
                },
            }
            return ConversationResponse(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=message,
                response_type=response_type,
                intent=intent,
                confirmation_required=confirmation_required,
                blocked=blocked,
                warnings=result.warnings,
                audit_metadata=result.audit_metadata,
                metadata=metadata,
            )

        message = self.personal_assistant.calendar_service.format_result(result)
        draft = result.event_draft
        action_type = {
            CalendarOperation.QUERY: "calendar.query",
            CalendarOperation.DRAFT_EVENT: "calendar.event_draft",
            CalendarOperation.LIST_LOCAL: "calendar.list_local",
            CalendarOperation.CANCEL_DRAFT: "calendar.cancel_draft",
        }.get(result.operation, "calendar.unknown")
        risk_level = "safe_readonly"
        response_type = ConversationResponseType.ANSWER
        confirmation_required = False
        blocked = False
        decision_status = result.status.value
        if result.status is CalendarStatus.PENDING_CONFIRMATION:
            risk_level = "medium"
            response_type = ConversationResponseType.CONFIRMATION_REQUIRED
            confirmation_required = True
            decision_status = "confirmation_required"
        elif result.status is CalendarStatus.SAFE_QUERY_PREVIEW:
            response_type = ConversationResponseType.ACTION_PREVIEW
        elif result.status is CalendarStatus.BLOCKED:
            risk_level = "blocked"
            response_type = ConversationResponseType.BLOCKED
            blocked = True
        intent = {
            "category": action_type,
            "target": draft.title if draft is not None else result.query.date_text if result.query is not None else "",
            "requires_clarification": False,
        }
        metadata = {
            "source": request.source.value,
            "action_type": action_type,
            "risk_level": risk_level,
            "target": draft.title if draft is not None else result.query.date_text if result.query is not None else "",
            "decision_status": decision_status,
            "personal_assistant": {
                "scope": "calendar",
                "operation": result.operation.value,
                "status": result.status.value,
                "target": draft.title if draft is not None else result.query.date_text if result.query is not None else "",
                "risk_level": risk_level,
                "panel_title": "Calendar draft preview" if result.operation is CalendarOperation.DRAFT_EVENT else "Calendar query preview",
                "panel_summary": message,
            },
        }
        return ConversationResponse(
            session_id=request.session_id,
            user_message=request.message,
            assistant_message=message,
            response_type=response_type,
            intent=intent,
            confirmation_required=confirmation_required,
            blocked=blocked,
            warnings=result.warnings,
            audit_metadata=result.audit_metadata,
            metadata=metadata,
        )

    def _is_device_like(self, message: str, candidate) -> bool:
        normalized = message.lower()
        if candidate is not None:
            action_type_value = getattr(candidate.action_type, "value", str(candidate.action_type))
            if action_type_value.startswith("device."):
                return True
        return any(token in normalized for token in ("isik", "ışık", "lamba", "klima", "kamera", "kapi", "kapı"))

    def _build_device_response(self, request: ConversationRequest, intent_res: dict[str, Any], action_candidate, permission_decision):
        device_result = self.device_planner.preview_device_action(request.message, source=request.source)
        if device_result.status is DeviceRegistryStatus.AMBIGUOUS:
            candidate_labels = [device.display_name for device in device_result.resolution.candidates] if device_result.resolution else []
            prompt = "Hangi cihazi kastettigini belirtmelisin."
            if candidate_labels:
                prompt = f"Hangi cihazi kastettigini belirtmelisin: {', '.join(candidate_labels)}."
            return ConversationResponse(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=prompt,
                response_type=ConversationResponseType.CLARIFICATION,
                intent=intent_res,
                action_candidate=action_candidate,
                permission_decision=permission_decision,
                clarification_required=True,
                warnings=device_result.warnings,
                metadata={"device_result_status": device_result.status.value},
            )
        if device_result.status in {DeviceRegistryStatus.BLOCKED, DeviceRegistryStatus.UNSUPPORTED}:
            return ConversationResponse(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=device_result.message,
                response_type=ConversationResponseType.BLOCKED,
                intent=intent_res,
                action_candidate=action_candidate,
                permission_decision=permission_decision,
                blocked=True,
                warnings=device_result.warnings,
                metadata={"device_result_status": device_result.status.value},
            )
        if device_result.plan is not None:
            return ConversationResponse(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=device_result.message,
                response_type=ConversationResponseType.CONFIRMATION_REQUIRED if device_result.plan.requires_confirmation else ConversationResponseType.ACTION_PREVIEW,
                intent=intent_res,
                action_candidate=action_candidate,
                permission_decision=permission_decision,
                confirmation_required=device_result.plan.requires_confirmation,
                warnings=device_result.warnings,
                metadata={
                    "device_result_status": device_result.status.value,
                    "device_plan": asdict(device_result.plan),
                },
            )
        return None

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
