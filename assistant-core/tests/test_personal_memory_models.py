from app.personal_memory.models import (
    PersonalMemoryItem, MemoryType, MemorySensitivity, PreferenceMemory
)

def test_personal_memory_item_creation():
    item = PersonalMemoryItem(
        memory_id="123",
        memory_type=MemoryType.PREFERENCE,
        key="browser",
        value="chrome",
        sensitivity=MemorySensitivity.NORMAL
    )
    assert item.memory_id == "123"
    assert item.memory_type == MemoryType.PREFERENCE
    assert item.value == "chrome"

def test_preference_memory():
    pref = PreferenceMemory(key="browser", value="chrome")
    assert pref.key == "browser"
    assert pref.category == "general"
