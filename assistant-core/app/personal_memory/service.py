import uuid
from typing import Optional
from app.personal_memory.models import (
    MemoryOperation, MemoryOperationResult, MemoryOperationStatus,
    MemoryType, PersonalMemoryItem, MemorySource
)
from app.personal_memory.store import get_store
from app.personal_memory.policy import SensitiveMemoryPolicy
from app.personal_memory.intents import MemoryIntentParser

class PersonalMemoryService:
    def __init__(self):
        self.store = get_store()
        
    def handle_text(self, text: str) -> MemoryOperationResult:
        operation, value, m_type = MemoryIntentParser.parse(text)
        
        if operation == MemoryOperation.UNKNOWN:
            return MemoryOperationResult(
                status=MemoryOperationStatus.INVALID,
                operation=MemoryOperation.UNKNOWN,
                message="Geçerli bir hafıza işlemi bulunamadı."
            )
            
        if operation == MemoryOperation.SHOW:
            return self.show(m_type)
            
        if operation == MemoryOperation.FORGET:
            return self.forget(value or "last_item")
            
        if operation == MemoryOperation.REMEMBER:
            if not value:
                value = text
            if SensitiveMemoryPolicy.is_blocked(value, m_type):
                return MemoryOperationResult(
                    status=MemoryOperationStatus.BLOCKED,
                    operation=MemoryOperation.REMEMBER,
                    blocked_reason=SensitiveMemoryPolicy.build_blocked_reason(value),
                    message="Güvenlik politikası gereği bu bilgi hafızaya alınamaz."
                )
            
            # Simple MVP implementation: use the value as both key and value if not structured
            return self.remember(key=value, value=value, memory_type=m_type)
            
        return MemoryOperationResult(
            status=MemoryOperationStatus.INVALID,
            operation=operation,
            message="Desteklenmeyen hafıza işlemi."
        )

    def remember(self, key: str, value: str, memory_type: MemoryType = MemoryType.PREFERENCE, source: MemorySource = MemorySource.EXPLICIT_USER_REQUEST) -> MemoryOperationResult:
        if SensitiveMemoryPolicy.is_blocked(value, memory_type):
            return MemoryOperationResult(
                status=MemoryOperationStatus.BLOCKED,
                operation=MemoryOperation.REMEMBER,
                blocked_reason=SensitiveMemoryPolicy.build_blocked_reason(value),
                message="Güvenlik politikası gereği bu bilgi hafızaya alınamaz."
            )
            
        item = PersonalMemoryItem(
            memory_id=str(uuid.uuid4()),
            memory_type=memory_type,
            key=key,
            value=value,
            source=source
        )
        
        saved_item = self.store.add(item)
        return MemoryOperationResult(
            status=MemoryOperationStatus.STORED,
            operation=MemoryOperation.REMEMBER,
            memory_item=saved_item,
            affected_count=1,
            message=f"Hafızaya alındı: {value}"
        )

    def forget(self, key_or_id: str) -> MemoryOperationResult:
        if not key_or_id:
            return MemoryOperationResult(
                status=MemoryOperationStatus.INVALID,
                operation=MemoryOperation.FORGET,
                message="Silinecek hafıza anahtarı belirtilmedi."
            )
            
        success = self.store.forget(key_or_id)
        if success:
            return MemoryOperationResult(
                status=MemoryOperationStatus.FORGOTTEN,
                operation=MemoryOperation.FORGET,
                affected_count=1,
                message=f"Hafızadan silindi: {key_or_id}"
            )
        return MemoryOperationResult(
            status=MemoryOperationStatus.NOT_FOUND,
            operation=MemoryOperation.FORGET,
            message=f"Hafızada bulunamadı: {key_or_id}"
        )

    def show(self, memory_type: MemoryType = MemoryType.UNKNOWN) -> MemoryOperationResult:
        m_type_filter = memory_type if memory_type != MemoryType.UNKNOWN else None
        items = self.store.list_all(m_type_filter)
        
        if not items:
            return MemoryOperationResult(
                status=MemoryOperationStatus.SHOWN,
                operation=MemoryOperation.SHOW,
                affected_count=0,
                message="Hafızada henüz bir şey yok."
            )
            
        lines = [f"- {item.memory_type.value}: {item.value}" for item in items]
        summary = "Hatırladıklarım:\n" + "\n".join(lines)
        return MemoryOperationResult(
            status=MemoryOperationStatus.SHOWN,
            operation=MemoryOperation.SHOW,
            affected_count=len(items),
            message=summary
        )
