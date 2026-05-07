import re
from typing import Optional, Tuple

from app.personal_memory.models import MemoryOperation, MemoryType


class MemoryIntentParser:
    @staticmethod
    def _normalize(text: str) -> str:
        normalized = text.lower().strip()
        return normalized.translate(str.maketrans({"ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u"}))

    @classmethod
    def parse(cls, text: str) -> Tuple[MemoryOperation, Optional[str], MemoryType]:
        normalized = cls._normalize(text)
        original = text.strip()

        if "neleri hatirliyorsun" in normalized or "hafizani goster" in normalized:
            return MemoryOperation.SHOW, None, MemoryType.UNKNOWN
        if "cihaz takma adlarini goster" in normalized:
            return MemoryOperation.SHOW, None, MemoryType.DEVICE_ALIAS
        if "tercihlerimi goster" in normalized:
            return MemoryOperation.SHOW, None, MemoryType.PREFERENCE

        forget_match = re.search(r"(.+?)\s+bilgisini unut$", normalized)
        if forget_match:
            return MemoryOperation.FORGET, forget_match.group(1).strip(), MemoryType.UNKNOWN
        forget_alias_match = re.search(r"(.+?)\s+takma adini unut$", normalized)
        if forget_alias_match:
            return MemoryOperation.FORGET, forget_alias_match.group(1).strip(), MemoryType.UNKNOWN
        if normalized.startswith("bunu unut") or normalized.startswith("sunu unut"):
            return MemoryOperation.FORGET, "last_item", MemoryType.UNKNOWN

        remember_prefix = re.search(r"(?:bunu hatirla|sunu hatirla|hatirla)[:\s]+(.+)$", normalized)
        if remember_prefix:
            if ":" in original:
                value = original.split(":", 1)[1].strip()
            else:
                value = original.split(maxsplit=1)[1].strip() if len(original.split(maxsplit=1)) > 1 else original
            return MemoryOperation.REMEMBER, value, cls._memory_type(normalized)

        remember_state = re.search(r"(.+?)\s+(?:oldugunu|olarak)\s+hatirla$", normalized)
        if remember_state:
            original_match = re.search(r"(.+?)\s+(?:olduğunu|oldugunu|olarak)\s+hatırla$", original, flags=re.IGNORECASE)
            value = original_match.group(1).strip() if original_match else original
            return MemoryOperation.REMEMBER, value, cls._memory_type(normalized)

        prefer_match = re.search(r"ben\s+(.+?)\s+severim$", normalized)
        if prefer_match:
            original_match = re.search(r"ben\s+(.+?)\s+severim$", original, flags=re.IGNORECASE)
            value = original_match.group(1).strip() if original_match else original
            return MemoryOperation.REMEMBER, value, MemoryType.PREFERENCE

        if normalized.endswith("demeyi tercih ederim"):
            return MemoryOperation.REMEMBER, normalized.replace("demeyi tercih ederim", "").strip(), MemoryType.PREFERENCE

        if normalized.endswith("ana isik de"):
            return MemoryOperation.REMEMBER, normalized, MemoryType.DEVICE_ALIAS
        if normalized.endswith("ofis de"):
            return MemoryOperation.REMEMBER, normalized, MemoryType.ROOM_ALIAS

        return MemoryOperation.UNKNOWN, None, MemoryType.UNKNOWN

    @classmethod
    def _memory_type(cls, normalized: str) -> MemoryType:
        if "isik" in normalized or "cihaz" in normalized or "ana isik" in normalized:
            return MemoryType.DEVICE_ALIAS
        if "oda" in normalized or "ofis de" in normalized:
            return MemoryType.ROOM_ALIAS
        return MemoryType.PREFERENCE
