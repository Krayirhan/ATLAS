from typing import Optional
from app.conversation.models import ConversationState

class StateManager:
    """In-memory MVP conversation state manager."""
    
    def __init__(self):
        self._states: dict[str, ConversationState] = {}
        
    def get_state(self, session_id: str) -> ConversationState:
        if session_id not in self._states:
            self._states[session_id] = ConversationState(session_id=session_id)
        return self._states[session_id]
        
    def save_state(self, state: ConversationState) -> None:
        self._states[state.session_id] = state
        
    def reset_session(self, session_id: str) -> ConversationState:
        new_state = ConversationState(session_id=session_id)
        self._states[session_id] = new_state
        return new_state

_global_state_manager = StateManager()

def get_state_manager() -> StateManager:
    return _global_state_manager
