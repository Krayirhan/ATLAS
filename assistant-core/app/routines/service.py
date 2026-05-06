import re
from typing import Optional, Tuple
from app.routines.engine import RoutineEngine
from app.routines.models import RoutinePreview, RoutineResult

class RoutineService:
    def __init__(self):
        self.engine = RoutineEngine()
        
    def parse_routine_request(self, text: str) -> Tuple[Optional[str], str]:
        text_lower = text.lower().strip()
        
        # Check list routines
        if "rutinleri göster" in text_lower or "hangi rutinler var" in text_lower:
            return None, "list"
            
        # Extract routine name
        match = re.search(r"([\w\sçğıöşü]+)\s+(?:modunu\s+başlat|moduna\s+geç|modunu\s+aç|modunu\s+önizle)", text_lower)
        if match:
            return match.group(1).strip() + " modu", "run"
            
        if "eve geldim" in text_lower:
            return "eve geldim", "run"
            
        if "evden çıkıyorum" in text_lower:
            return "evden çıkıyorum", "run"
            
        return None, "unknown"

    def handle_text(self, text: str) -> str:
        routine_name, operation = self.parse_routine_request(text)
        
        if operation == "list":
            routines = self.engine.list_routines()
            lines = [f"- {r.display_name} ({len(r.steps)} adım)" for r in routines]
            return "Kullanılabilir rutinler:\n" + "\n".join(lines)
            
        if operation == "run" and routine_name:
            result = self.engine.run_routine(routine_name)
            if result.status == "blocked":
                return result.message
            if result.status == "awaiting_confirmation":
                return result.message
            return result.message
            
        return "Rutin anlaşılamadı veya desteklenmiyor."
