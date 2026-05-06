import re
from app.personal_memory.models import MemorySensitivity, MemoryType, PersonalMemoryItem

class SensitiveMemoryPolicy:
    
    BLOCKED_KEYWORDS = [
        "şifre", "password", "token", "api key", "secret", "private key", 
        "tc kimlik", "kredi kartı", "banka şifresi", "seed phrase", "recovery code"
    ]
    
    @classmethod
    def classify_sensitivity(cls, text: str, memory_type: MemoryType) -> MemorySensitivity:
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in cls.BLOCKED_KEYWORDS):
            return MemorySensitivity.BLOCKED
        if memory_type == MemoryType.PREFERENCE:
            return MemorySensitivity.NORMAL
        return MemorySensitivity.NORMAL

    @classmethod
    def is_blocked(cls, text: str, memory_type: MemoryType) -> bool:
        return cls.classify_sensitivity(text, memory_type) == MemorySensitivity.BLOCKED

    @classmethod
    def requires_confirmation(cls, item: PersonalMemoryItem) -> bool:
        return item.sensitivity in [MemorySensitivity.PRIVATE, MemorySensitivity.SENSITIVE]

    @classmethod
    def sanitize_value(cls, value: str) -> str:
        return value

    @classmethod
    def build_blocked_reason(cls, text: str) -> str:
        return "İçerisinde hassas veya yasaklı bilgiler bulunduğu için (örn: şifre, token) güvenlik politikası gereği bu hafıza işlemi engellendi."
