from app.conversation.loop import ConversationLoop
from app.conversation.models import ConversationResponseType


def test_conversation_loop_chrome():
    loop = ConversationLoop()
    response = loop.handle_text("Chrome'u aç", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.ACTION_PREVIEW
    assert "Chrome" in response.assistant_message
    assert response.pc_plan is not None
    assert response.pc_plan.dry_run is True


def test_conversation_loop_blocked():
    loop = ConversationLoop()
    response = loop.handle_text("Şifrelerimi oku", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.BLOCKED
    assert response.blocked is True


def test_conversation_loop_clarification():
    loop = ConversationLoop()
    response = loop.handle_text("Işığı aç", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.CLARIFICATION
    assert response.clarification_required is True


def test_conversation_loop_confirmation():
    loop = ConversationLoop()
    response = loop.handle_text("Bilgisayarı kapat", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.CONFIRMATION_REQUIRED
    assert response.confirmation_required is True


def test_conversation_loop_answer():
    loop = ConversationLoop()
    response = loop.handle_text("ATLAS şu an ne durumda?", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.ANSWER


def test_conversation_loop_state_management():
    loop = ConversationLoop()
    session_id = "test-session"
    loop.handle_text("Chrome'u aç", session_id=session_id)
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
    response = loop.handle_text("Bunu hatırla: Chrome kullanırım", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.ANSWER
    assert "chrome" in response.assistant_message.lower()


def test_conversation_loop_memory_blocked():
    loop = ConversationLoop()
    response = loop.handle_text("Şifrem 1234 olduğunu hatırla", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.BLOCKED


def test_conversation_loop_routine_confirmation():
    loop = ConversationLoop()
    response = loop.handle_text("Çalışma modunu başlat", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.CONFIRMATION_REQUIRED


def test_conversation_loop_routine_list():
    loop = ConversationLoop()
    response = loop.handle_text("Rutinleri göster", project_name="ATLAS")
    assert response.response_type == ConversationResponseType.ANSWER
    assert "Çalışma Modu" in response.assistant_message
