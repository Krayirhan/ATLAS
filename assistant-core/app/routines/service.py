import re
from typing import Optional, Tuple

from app.routines.engine import RoutineEngine
from app.routines.models import RoutineDefinition, RoutinePreview, RoutineResult, RoutineStatus


class RoutineService:
    def __init__(self):
        self.engine = RoutineEngine()

    def parse_routine_request(self, text: str) -> Tuple[Optional[str], str]:
        text_lower = text.lower().strip()

        if "rutinleri goster" in text_lower or "hangi rutinler var" in text_lower or "rutinleri göster" in text_lower:
            return None, "list"

        match = re.search(r"([\w\sçğıöşü]+)\s+(?:modunu\s+baslat|modunu\s+başlat|moduna\s+gec|moduna\s+geç|modunu\s+ac|modunu\s+aç|modunu\s+onizle|modunu\s+önizle)", text_lower)
        if match:
            routine_name = match.group(1).strip()
            if not routine_name.endswith(" modu"):
                routine_name = f"{routine_name} modu"
            if "onizle" in text_lower or "önizle" in text_lower:
                return routine_name, "preview"
            return routine_name, "run"

        if "eve geldim" in text_lower:
            return "eve geldim", "run"
        if "evden cikiyorum" in text_lower or "evden çıkıyorum" in text_lower:
            return "evden cikiyorum", "run"

        return None, "unknown"

    def handle_text(self, text: str):
        routine_name, operation = self.parse_routine_request(text)

        if operation == "list":
            return self.engine.list_routines()
        if operation == "preview" and routine_name:
            return self.engine.preview_routine(routine_name)
        if operation == "run" and routine_name:
            return self.engine.run_routine(routine_name)
        return None

    def format_response(self, result) -> str:
        if result is None:
            return "Rutin anlasilamadi veya desteklenmiyor."
        if isinstance(result, list):
            lines = [f"- {routine.display_name} ({len(routine.steps)} adim)" for routine in result]
            return "Kullanilabilir rutinler:\n" + "\n".join(lines)
        if isinstance(result, RoutinePreview):
            lines = [
                f"Rutin onizleme: {result.routine_name}",
                f"Risk: {result.risk_level}",
                f"Onay gerekli: {'evet' if result.requires_confirmation else 'hayir'}",
                f"Engelli: {'evet' if result.blocked else 'hayir'}",
            ]
            for step in result.steps:
                lines.append(f"- {step.label} ({step.action_type})")
            return "\n".join(lines)
        if isinstance(result, RoutineResult):
            if result.status == RoutineStatus.BLOCKED:
                return result.message
            if result.status == RoutineStatus.AWAITING_CONFIRMATION:
                return result.message
            return result.message
        if isinstance(result, RoutineDefinition):
            return f"{result.display_name} ({len(result.steps)} adim)"
        return str(result)
