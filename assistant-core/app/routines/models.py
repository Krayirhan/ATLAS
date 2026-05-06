from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field

def _utcnow():
    return datetime.now(timezone.utc)

class RoutineCategory(str, Enum):
    WORK = "work"
    SLEEP = "sleep"
    MEETING = "meeting"
    GAMING = "gaming"
    LEAVING_HOME = "leaving_home"
    ARRIVING_HOME = "arriving_home"
    CUSTOM = "custom"
    UNKNOWN = "unknown"

class RoutineSource(str, Enum):
    BUILT_IN = "built_in"
    USER_CREATED = "user_created"
    MEMORY = "memory"
    IMPORT_FILE = "import_file"
    SYSTEM = "system"

class RoutineStatus(str, Enum):
    PREVIEWED = "previewed"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class RoutineStep(BaseModel):
    step_id: str
    order: int
    label: str
    action_type: str
    target: Optional[str] = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    risk_level: str = "low"
    optional: bool = False
    requires_confirmation: bool = False
    dry_run_supported: bool = True
    expected_result: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class RoutineDefinition(BaseModel):
    routine_id: str
    name: str
    display_name: str
    description: str
    category: RoutineCategory
    steps: list[RoutineStep] = Field(default_factory=list)
    enabled: bool = True
    source: RoutineSource = RoutineSource.BUILT_IN
    risk_level: str = "low"
    requires_confirmation: bool = False
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

class RoutinePreview(BaseModel):
    routine_id: str
    routine_name: str
    summary: str
    steps: list[RoutineStep] = Field(default_factory=list)
    risk_level: str
    requires_confirmation: bool
    blocked: bool
    blocked_reason: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)
    permission_decisions: dict[str, Any] = Field(default_factory=dict)
    safe_to_run: bool
    estimated_effect: str
    audit_metadata: dict[str, Any] = Field(default_factory=dict)

class RoutineStepResult(BaseModel):
    step_id: str
    status: str
    executed: bool
    message: str
    action_preview: Optional[Any] = None
    permission_decision: Optional[Any] = None
    audit_metadata: dict[str, Any] = Field(default_factory=dict)

class RoutineResult(BaseModel):
    routine_id: str
    status: RoutineStatus
    executed: bool
    dry_run: bool
    message: str
    step_results: list[RoutineStepResult] = Field(default_factory=list)
    blocked_reason: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)
    audit_metadata: dict[str, Any] = Field(default_factory=dict)
