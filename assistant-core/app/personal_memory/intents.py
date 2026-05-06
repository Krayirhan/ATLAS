import re
from typing import Optional, Tuple
from app.personal_memory.models import MemoryOperation, MemoryType

class MemoryIntentParser:
    
    REMEMBER_PATTERNS = [
        r"(?:bunu\s+hatırla|şunu\s+hatırla|hatırla)[:\s]+(.*)",
        r"benim\s+tercihimi\s+hatırla[:\s]+(.*)",
        r"(.*)\s+(?:olduğunu|olarak)\s+hatırla",
        r"ben\s+(.*)\s+severim",
        r"(.*)\s+demeyi\s+tercih\s+ederim",
        r"(.*)\s+ana\s+ışık\s+de",
        r"(.*)\s+(?:odasına|kısmına)\s+ofis\s+de"
    ]
    
    FORGET_PATTERNS = [
        r"(?:bunu|şunu)\s+unut",
        r"(.*)\s+bilgisini\s+unut",
        r"hafızadan\s+(.*)'i\s+sil",
        r"(.*)\s+takma\s+adını\s+unut"
    ]
    
    SHOW_PATTERNS = [
        r"neleri\s+hatırlıyorsun",
        r"hafızanı\s+göster",
        r"cihaz\s+takma\s+adlarını\s+göster",
        r"tercihlerimi\s+göster"
    ]
    
    @classmethod
    def parse(cls, text: str) -> Tuple[MemoryOperation, Optional[str], MemoryType]:
        text_lower = text.lower().strip()
        
        # Check SHOW
        for pattern in cls.SHOW_PATTERNS:
            if re.search(pattern, text_lower):
                m_type = MemoryType.UNKNOWN
                if "cihaz" in text_lower:
                    m_type = MemoryType.DEVICE_ALIAS
                elif "tercih" in text_lower:
                    m_type = MemoryType.PREFERENCE
                return MemoryOperation.SHOW, None, m_type
                
        # Check FORGET
        for pattern in cls.FORGET_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                key = match.group(1).strip() if match.groups() and match.group(1) else None
                return MemoryOperation.FORGET, key, MemoryType.UNKNOWN
                
        # Check REMEMBER
        for pattern in cls.REMEMBER_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                val = match.group(1).strip() if match.groups() and match.group(1) else text
                m_type = MemoryType.PREFERENCE
                if "ışık" in text_lower or "cihaz" in text_lower or "de" in text_lower:
                    m_type = MemoryType.DEVICE_ALIAS
                elif "oda" in text_lower:
                    m_type = MemoryType.ROOM_ALIAS
                return MemoryOperation.REMEMBER, val, m_type
                
        return MemoryOperation.UNKNOWN, None, MemoryType.UNKNOWN
