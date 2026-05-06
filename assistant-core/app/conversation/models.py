from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.actions.models import ActionCandidate, PermissionDecision, ActionPreview
from app.actions.types import ActionType, ActionSource
from app.control.models import PCControlPlan

class ConversationResponseType(str, Enum):
    ANSWER = "answer"
    ACTION_PREVIEW = "action_preview"
    CLARIFICATION = "clarification"
    CONFIRMATION_REQUIRED = "confirmation_required"
    BLOCKED = "blocked"
    UNSUPPORTED = "unsupported"
    ERROR = "error"

class ConversationRequest(BaseModel):
    project_name: str
    message: str
    source: ActionSource = ActionSource.TEXT
    session_id: str
    language: str = "tr"
    metadata: dict[str, Any] = Field(default_factory=dict)

class ConversationResponse(BaseModel):
    session_id: str
    user_message: str
    assistant_message: str
    response_type: ConversationResponseType
    intent: Optional[dict[str, Any]] = None
    action_candidate: Optional[ActionCandidate] = None
    permission_decision: Optional[PermissionDecision] = None
    pc_plan: Optional[PCControlPlan] = None
    clarification_required: bool = False
    confirmation_required: bool = False
    blocked: bool = False
    warnings: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    audit_metadata: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

def _utcnow():
    return datetime.now(timezone.utc)

class ConversationTurn(BaseModel):
    turn_id: str
    session_id: str
    user_message: str
    assistant_message: str
    intent_category: str
    action_type: str
    decision_status: str
    created_at: datetime = Field(default_factory=_utcnow)

class ConversationState(BaseModel):
    session_id: str
    last_intent: Optional[str] = None
    last_action: Optional[str] = None
    pending_clarification: bool = False
    pending_confirmation: bool = False
    turns: list[ConversationTurn] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
