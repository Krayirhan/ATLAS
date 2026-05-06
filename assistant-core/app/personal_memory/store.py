import uuid
from typing import Optional
from app.personal_memory.models import PersonalMemoryItem, MemoryType

class InMemoryPersonalMemoryStore:
    def __init__(self):
        self._items: dict[str, PersonalMemoryItem] = {}

    def add(self, item: PersonalMemoryItem) -> PersonalMemoryItem:
        if not item.memory_id:
            item.memory_id = str(uuid.uuid4())
        self._items[item.memory_id] = item
        return item

    def update(self, memory_id: str, value: str) -> Optional[PersonalMemoryItem]:
        if memory_id in self._items:
            self._items[memory_id].value = value
            return self._items[memory_id]
        return None

    def forget(self, memory_id_or_key: str) -> bool:
        to_delete = []
        for mid, item in self._items.items():
            if mid == memory_id_or_key or item.key == memory_id_or_key:
                to_delete.append(mid)
        for mid in to_delete:
            del self._items[mid]
        return len(to_delete) > 0

    def find_by_key(self, key: str) -> list[PersonalMemoryItem]:
        return [item for item in self._items.values() if item.key == key]

    def list_all(self, memory_type: Optional[MemoryType] = None) -> list[PersonalMemoryItem]:
        if memory_type:
            return [item for item in self._items.values() if item.memory_type == memory_type]
        return list(self._items.values())

    def clear(self, memory_type: Optional[MemoryType] = None) -> int:
        to_delete = []
        for mid, item in self._items.items():
            if memory_type is None or item.memory_type == memory_type:
                to_delete.append(mid)
        for mid in to_delete:
            del self._items[mid]
        return len(to_delete)

_global_store = InMemoryPersonalMemoryStore()

def get_store() -> InMemoryPersonalMemoryStore:
    return _global_store
