from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field

class MemoryType(str, Enum):
    PREFERENCE = "preference"
    DEVICE_ALIAS = "device_alias"
    ROOM_ALIAS = "room_alias"
    ROUTINE_PREFERENCE = "routine_preference"
    REMINDER_PREFERENCE = "reminder_preference"
    ASSISTANT_SETTING = "assistant_setting"
    USER_NOTE = "user_note"
    UNKNOWN = "unknown"

class MemorySensitivity(str, Enum):
    PUBLIC = "public"
    NORMAL = "normal"
    PRIVATE = "private"
    SENSITIVE = "sensitive"
    BLOCKED = "blocked"

class MemorySource(str, Enum):
    EXPLICIT_USER_REQUEST = "explicit_user_request"
    CONVERSATION = "conversation"
    SETTINGS = "settings"
    IMPORT_FILE = "import_file"
    SYSTEM = "system"
    UNKNOWN = "unknown"

class MemoryOperation(str, Enum):
    REMEMBER = "remember"
    FORGET = "forget"
    SHOW = "show"
    UPDATE = "update"
    CLEAR = "clear"
    EXPORT_PREVIEW = "export_preview"
    UNKNOWN = "unknown"

class MemoryOperationStatus(str, Enum):
    STORED = "stored"
    UPDATED = "updated"
    FORGOTTEN = "forgotten"
    SHOWN = "shown"
    BLOCKED = "blocked"
    NEEDS_CONFIRMATION = "needs_confirmation"
    NOT_FOUND = "not_found"
    INVALID = "invalid"
    SKIPPED = "skipped"

def _utcnow():
    return datetime.now(timezone.utc)

class PersonalMemoryItem(BaseModel):
    memory_id: str
    memory_type: MemoryType
    key: str
    value: Any
    source: MemorySource = MemorySource.EXPLICIT_USER_REQUEST
    sensitivity: MemorySensitivity = MemorySensitivity.NORMAL
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    expires_at: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list)
    user_confirmed: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

class PreferenceMemory(BaseModel):
    key: str
    value: Any
    category: str = "general"
    confidence: float = 1.0
    user_confirmed: bool = True

class DeviceAliasMemory(BaseModel):
    alias: str
    canonical_name: str
    room: Optional[str] = None
    device_type: Optional[str] = None
    capabilities: list[str] = Field(default_factory=list)

class RoomAliasMemory(BaseModel):
    alias: str
    canonical_name: str

class RoutinePreferenceMemory(BaseModel):
    routine_name: str
    preferred_time: Optional[str] = None
    preferred_mode: Optional[str] = None
    enabled: bool = True
    notes: Optional[str] = None

class MemoryOperationResult(BaseModel):
    status: MemoryOperationStatus
    operation: MemoryOperation
    memory_item: Optional[PersonalMemoryItem] = None
    affected_count: int = 0
    message: str = ""
    warnings: list[str] = Field(default_factory=list)
    blocked_reason: Optional[str] = None
    audit_metadata: dict[str, Any] = Field(default_factory=dict)
