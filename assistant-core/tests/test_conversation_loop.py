from app.conversation.loop import ConversationLoop
from app.conversation.models import ConversationResponseType
import app.personal_assistant.store as personal_assistant_store


def test_conversation_loop_chrome():
    loop = ConversationLoop()
    response = loop.handle_text("Chrome'u ac", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.ACTION_PREVIEW
    assert "Chrome" in response.assistant_message
    assert response.pc_plan is not None
    assert response.pc_plan.dry_run is True


def test_conversation_loop_blocked():
    loop = ConversationLoop()
    response = loop.handle_text("Sifrelerimi oku", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.BLOCKED
    assert response.blocked is True


def test_conversation_loop_clarification():
    loop = ConversationLoop()
    response = loop.handle_text("Isigi ac", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.CLARIFICATION
    assert response.clarification_required is True


def test_conversation_loop_confirmation():
    loop = ConversationLoop()
    response = loop.handle_text("Bilgisayari kapat", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.CONFIRMATION_REQUIRED
    assert response.confirmation_required is True


def test_conversation_loop_answer():
    loop = ConversationLoop()
    response = loop.handle_text("ATLAS su an ne durumda?", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.ANSWER


def test_conversation_loop_state_management():
    loop = ConversationLoop()
    session_id = "test-session"
    loop.handle_text("Chrome'u ac", session_id=session_id)
    state = loop.get_state(session_id)
    assert state.last_intent == "pc.open_app"
    assert state.last_action == "pc.open_app"
    assert len(state.turns) == 1

    loop.reset_session(session_id)
    state = loop.get_state(session_id)
    assert state.last_intent is None
    assert len(state.turns) == 0


def test_conversation_loop_memory_remember():
    loop = ConversationLoop()
    response = loop.handle_text("Bunu hatirla: Chrome kullanirim", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.ANSWER
    assert "chrome" in response.assistant_message.lower()


def test_conversation_loop_memory_blocked():
    loop = ConversationLoop()
    response = loop.handle_text("Sifrem 1234 oldugunu hatirla", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.BLOCKED


def test_conversation_loop_routine_confirmation():
    loop = ConversationLoop()
    response = loop.handle_text("Calisma modunu baslat", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.CONFIRMATION_REQUIRED


def test_conversation_loop_routine_list():
    loop = ConversationLoop()
    response = loop.handle_text("Rutinleri goster", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.ANSWER
    assert "Modu" in response.assistant_message


def test_conversation_loop_device_confirmation():
    loop = ConversationLoop()
    response = loop.handle_text("Salon isigini ac", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.CONFIRMATION_REQUIRED


def test_conversation_loop_device_clarification():
    loop = ConversationLoop()
    response = loop.handle_text("Isigi ac", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.CLARIFICATION
    assert "Salon Isigi" in response.assistant_message


def test_conversation_loop_device_temperature_confirmation():
    loop = ConversationLoop()
    response = loop.handle_text("Klimayi 24 derece yap", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.CONFIRMATION_REQUIRED


def test_conversation_loop_reminder_confirmation(tmp_path, monkeypatch):
    monkeypatch.setattr(personal_assistant_store, "_default_store_path", lambda: tmp_path / "personal-assistant.json")
    personal_assistant_store._global_store = None
    loop = ConversationLoop()
    response = loop.handle_text("Bana 20 dakika sonra su icmeyi hatirlat", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.CONFIRMATION_REQUIRED
    assert "scheduler" in response.assistant_message.lower()


def test_conversation_loop_reminder_list(tmp_path, monkeypatch):
    monkeypatch.setattr(personal_assistant_store, "_default_store_path", lambda: tmp_path / "personal-assistant.json")
    personal_assistant_store._global_store = None
    loop = ConversationLoop()
    loop.handle_text("Bana 20 dakika sonra su icmeyi hatirlat", project_name="ATLAS")
    response = loop.handle_text("Hatirlaticilarimi goster", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.ANSWER
    assert "Hatirlaticilar:" in response.assistant_message


def test_conversation_loop_calendar_query(tmp_path, monkeypatch):
    monkeypatch.setattr(personal_assistant_store, "_default_store_path", lambda: tmp_path / "personal-assistant.json")
    personal_assistant_store._global_store = None
    loop = ConversationLoop()
    response = loop.handle_text("Bugun takvimimde ne var?", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.ACTION_PREVIEW
    assert "Harici calendar entegrasyonu kapali" in response.assistant_message


def test_conversation_loop_calendar_draft(tmp_path, monkeypatch):
    monkeypatch.setattr(personal_assistant_store, "_default_store_path", lambda: tmp_path / "personal-assistant.json")
    personal_assistant_store._global_store = None
    loop = ConversationLoop()
    response = loop.handle_text("Yarin 10a toplanti ekle", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.CONFIRMATION_REQUIRED
