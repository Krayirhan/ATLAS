from app.personal_memory.service import PersonalMemoryService
from app.personal_memory.models import MemoryOperationStatus

def test_memory_remember_preference():
    service = PersonalMemoryService()
    service.store.clear()
    
    res = service.handle_text("Bunu hatırla: Chrome kullanırım")
    assert res.status == MemoryOperationStatus.STORED
    assert res.affected_count == 1
    
    items = service.store.list_all()
    assert len(items) == 1
    assert items[0].value.lower() == "chrome kullanırım"

def test_memory_blocked_password():
    service = PersonalMemoryService()
    service.store.clear()
    
    res = service.handle_text("Şifremin 1234 olduğunu hatırla")
    assert res.status == MemoryOperationStatus.BLOCKED
    assert res.blocked_reason is not None
    assert len(service.store.list_all()) == 0

def test_memory_show():
    service = PersonalMemoryService()
    service.store.clear()
    
    service.handle_text("Bunu hatırla: Oyun modunda sesi 30 yapmayı seviyorum")
    res = service.handle_text("Neleri hatırlıyorsun?")
    assert res.status == MemoryOperationStatus.SHOWN
    assert "oyun modunda" in res.message.lower()

def test_memory_forget():
    service = PersonalMemoryService()
    service.store.clear()
    
    service.handle_text("Bunu hatırla: karanlık tema severim")
    res = service.handle_text("karanlık tema severim bilgisini unut")
    assert res.status == MemoryOperationStatus.FORGOTTEN
    assert len(service.store.list_all()) == 0
