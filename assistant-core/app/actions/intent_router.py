"""Deterministic IntentRouter for Sprint 39.

This module converts user text into IntentResult, ActionCandidate, and
PermissionManager preview decisions without executing anything.
"""

from __future__ import annotations

import re
from uuid import uuid4

from app.actions.models import (
    ActionCandidate,
    ClarificationRequest,
    IntentPreviewResult,
    IntentResult,
)
from app.actions.permission import PermissionManager
from app.actions.risk import DEFAULT_ACTION_RISK, RiskLevel
from app.actions.types import ActionSource, ActionType, IntentCategory


APP_ALIASES = {
    "chrome": "Chrome",
    "spotify": "Spotify",
    "not defteri": "Not Defteri",
    "notepad": "Not Defteri",
    "vs code": "VS Code",
    "visual studio code": "VS Code",
    "hesap makinesi": "Hesap Makinesi",
}

FOLDER_ALIASES = {
    "belgeler": "Belgeler",
    "indirilenler": "Indirilenler",
    "masaustu": "Masaustu",
    "downloads": "Indirilenler",
}

ROUTINE_ALIASES = {
    "calisma modu": "calisma modu",
    "uyku modu": "uyku modu",
    "oyun modu": "oyun modu",
    "toplanti modu": "toplanti modu",
    "evden cikiyorum": "evden cikiyorum",
    "eve geldim": "eve geldim",
}

ROOM_ALIASES = (
    "salon",
    "yatak odasi",
    "mutfak",
    "calisma odasi",
    "koridor",
)

DEVICE_ALIASES = (
    "isik",
    "isig",
    "lamba",
    "klima",
    "kamera",
    "kapi",
)

BLOCKED_PATTERNS: list[tuple[re.Pattern[str], ActionType, str]] = [
    (re.compile(r"\b(tum dosyalari sil|dosyayi sil|su dosyayi sil|sunu sil)\b"), ActionType.FILE_DELETE, "Dosya silme MVP'de engellidir."),
    (re.compile(r"\bregistry\b"), ActionType.REGISTRY_EDIT, "Registry degisikligi ATLAS policy tarafindan engellidir."),
    (re.compile(r"\b(sifrelerimi oku|sifreleri oku|kimlik bilgilerimi oku)\b"), ActionType.SECRET_READ, "Secret veya kimlik bilgisi okuma engellidir."),
    (re.compile(r"\b(tum diski tara|tum dosyalari tara|full disk scan)\b"), ActionType.FULL_DISK_SCAN, "Tum disk tarama privacy ve scope riski nedeniyle engellidir."),
    (re.compile(r"(powershell|cmd /c|invoke-expression|&&|;|\|)"), ActionType.SHELL_EXECUTE_UNRESTRICTED, "Terminal benzeri veya sinirsiz komut istemi engellidir."),
]


class IntentRouter:
    """Rule-based text router for safe action preview generation."""

    def __init__(self, *, permission_manager: PermissionManager | None = None) -> None:
        self._permission_manager = permission_manager or PermissionManager()

    def parse_text(self, text: str, source: ActionSource = ActionSource.TEXT) -> IntentResult:
        raw_text = text.strip()
        normalized_text = self._normalize(raw_text)
        intent_id = f"intent-{uuid4().hex[:12]}"

        blocked = self._match_blocked(normalized_text)
        if blocked is not None:
            action_type, reason = blocked
            return IntentResult(
                intent_id=intent_id,
                category=IntentCategory.BLOCKED,
                confidence=0.97,
                language="tr",
                raw_text=raw_text,
                normalized_text=normalized_text,
                entities={},
                target=self._blocked_target(normalized_text),
                action_candidate=action_type,
                safety_notes=[reason],
            )

        ambiguous = self._match_ambiguous(normalized_text)
        if ambiguous is not None:
            return IntentResult(
                intent_id=intent_id,
                category=IntentCategory.AMBIGUOUS,
                confidence=0.38,
                language="tr",
                raw_text=raw_text,
                normalized_text=normalized_text,
                entities=ambiguous["entities"],
                target=ambiguous["target"],
                action_candidate=ambiguous["action_type"],
                ambiguity_reason=ambiguous["reason"],
                requires_clarification=True,
                safety_notes=["Ambiguous request; no execution path."],
                suggested_questions=ambiguous["questions"],
            )

        conversation = self._match_conversation(normalized_text)
        if conversation is not None:
            return IntentResult(
                intent_id=intent_id,
                category=conversation["category"],
                confidence=0.96,
                language="tr",
                raw_text=raw_text,
                normalized_text=normalized_text,
                entities={},
                target="assistant",
                action_candidate=None,
                safety_notes=["Read-only conversational intent."],
            )

        app_name = self._match_alias(normalized_text, APP_ALIASES)
        if app_name and self._contains_open_verb(normalized_text):
            return self._intent(
                intent_id=intent_id,
                category=IntentCategory.PC_OPEN_APP,
                raw_text=raw_text,
                normalized_text=normalized_text,
                confidence=0.95,
                entities={"app_name": app_name},
                target=app_name,
                action_type=ActionType.PC_OPEN_APP,
            )

        folder_name = self._match_alias(normalized_text, FOLDER_ALIASES)
        if folder_name and "klasor" in normalized_text and self._contains_open_verb(normalized_text):
            return self._intent(
                intent_id=intent_id,
                category=IntentCategory.PC_OPEN_FOLDER,
                raw_text=raw_text,
                normalized_text=normalized_text,
                confidence=0.95,
                entities={"folder_name": folder_name},
                target=folder_name,
                action_type=ActionType.PC_OPEN_FOLDER,
            )

        system_intent = self._match_system_info(normalized_text)
        if system_intent is not None:
            return system_intent(intent_id, raw_text, normalized_text)

        volume_intent = self._match_volume(normalized_text)
        if volume_intent is not None:
            return volume_intent(intent_id, raw_text, normalized_text)

        media_intent = self._match_media(normalized_text)
        if media_intent is not None:
            return media_intent(intent_id, raw_text, normalized_text)

        browser_intent = self._match_browser(normalized_text)
        if browser_intent is not None:
            return browser_intent(intent_id, raw_text, normalized_text)

        file_intent = self._match_file_search(normalized_text)
        if file_intent is not None:
            return file_intent(intent_id, raw_text, normalized_text)

        reminder_intent = self._match_reminder(normalized_text)
        if reminder_intent is not None:
            return reminder_intent(intent_id, raw_text, normalized_text)

        routine_intent = self._match_routine(normalized_text)
        if routine_intent is not None:
            return routine_intent(intent_id, raw_text, normalized_text)

        device_intent = self._match_device(normalized_text)
        if device_intent is not None:
            return device_intent(intent_id, raw_text, normalized_text)

        shutdown_intent = self._match_power_action(normalized_text)
        if shutdown_intent is not None:
            return shutdown_intent(intent_id, raw_text, normalized_text)

        return IntentResult(
            intent_id=intent_id,
            category=IntentCategory.UNKNOWN,
            confidence=0.15,
            language="tr",
            raw_text=raw_text,
            normalized_text=normalized_text,
            entities={},
            target="",
            action_candidate=None,
            requires_clarification=True,
            ambiguity_reason="Komut desteklenen veya net bir intent kategorisine eslesmedi.",
            safety_notes=["Unknown request; no execution path."],
            suggested_questions=["Ne yapmak istedigini daha net tarif eder misin?"],
        )

    def to_action_candidate(self, intent: IntentResult, source: ActionSource = ActionSource.TEXT) -> ActionCandidate | None:
        action_type = intent.action_candidate
        if action_type is None:
            return None

        target = intent.target
        parameters = dict(intent.entities)
        risk_level = RiskLevel.BLOCKED if intent.category is IntentCategory.BLOCKED else DEFAULT_ACTION_RISK.get(action_type, RiskLevel.MEDIUM)
        requires_confirmation = risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH}
        reversible = risk_level in {RiskLevel.SAFE_READONLY, RiskLevel.LOW, RiskLevel.MEDIUM}
        blocked_reason = ""
        if intent.category is IntentCategory.BLOCKED:
            blocked_reason = intent.safety_notes[0] if intent.safety_notes else "Blocked action."

        return ActionCandidate(
            action_id=f"action-{uuid4().hex[:12]}",
            action_type=action_type,
            target=target,
            parameters=parameters,
            source=source,
            user_goal=intent.raw_text,
            intent_category=intent.category,
            risk_level=risk_level,
            requires_confirmation=requires_confirmation,
            dry_run_supported=True,
            reversible=reversible,
            expected_result=self._expected_result(action_type, target, parameters),
            blocked_reason=blocked_reason,
            audit_metadata={
                "intent_id": intent.intent_id,
                "confidence": intent.confidence,
                "normalized_text": intent.normalized_text,
                "router": "intent-router-mvp",
            },
        )

    def preview(self, text: str, source: ActionSource = ActionSource.TEXT) -> IntentPreviewResult:
        intent = self.parse_text(text, source=source)
        action_candidate = self.to_action_candidate(intent, source=source)
        clarification = self._clarification_from_intent(intent)
        warnings = list(intent.safety_notes)

        if action_candidate is None:
            return IntentPreviewResult(
                raw_text=text,
                intent=intent,
                action_candidate=None,
                action_preview=None,
                permission_decision=None,
                clarification=clarification,
                warnings=warnings,
                metadata={
                    "router": "intent-router-mvp",
                    "source": source.value,
                    "llm_used": False,
                    "no_action_required": intent.category in {IntentCategory.CONVERSATION_QUESTION, IntentCategory.CONVERSATION_STATUS},
                },
            )

        action_preview = self._permission_manager.build_preview(action_candidate)
        permission_decision = self._permission_manager.decide(action_candidate)
        if permission_decision.status.value == "clarification_required" and clarification is None:
            clarification = ClarificationRequest(
                reason=permission_decision.reason,
                missing_fields=self._missing_fields(intent, action_candidate),
                candidate_targets=self._candidate_targets(intent),
                suggested_questions=intent.suggested_questions or [permission_decision.confirmation_prompt],
            )

        return IntentPreviewResult(
            raw_text=text,
            intent=intent,
            action_candidate=action_candidate,
            action_preview=action_preview,
            permission_decision=permission_decision,
            clarification=clarification,
            warnings=warnings + list(permission_decision.warnings),
            metadata={
                "router": "intent-router-mvp",
                "source": source.value,
                "llm_used": False,
            },
        )

    def _intent(
        self,
        *,
        intent_id: str,
        category: IntentCategory,
        raw_text: str,
        normalized_text: str,
        confidence: float,
        entities: dict[str, object],
        target: str,
        action_type: ActionType,
        safety_notes: list[str] | None = None,
    ) -> IntentResult:
        return IntentResult(
            intent_id=intent_id,
            category=category,
            confidence=confidence,
            language="tr",
            raw_text=raw_text,
            normalized_text=normalized_text,
            entities=entities,
            target=target,
            action_candidate=action_type,
            safety_notes=safety_notes or [],
        )

    def _match_blocked(self, normalized_text: str) -> tuple[ActionType, str] | None:
        for pattern, action_type, reason in BLOCKED_PATTERNS:
            if pattern.search(normalized_text):
                return action_type, reason
        return None

    def _match_ambiguous(self, normalized_text: str) -> dict[str, object] | None:
        if normalized_text in {"ac", "kapat", "onu ac", "modu baslat"}:
            return {
                "action_type": None,
                "reason": "Hedef veya islem yeterince net degil.",
                "questions": ["Hangi hedef veya modu kastettigini belirtir misin?"],
                "target": "",
                "entities": {},
            }
        if normalized_text == "isigi ac":
            return {
                "action_type": ActionType.DEVICE_TURN_ON,
                "reason": "Hangi isigin acilacagi belirsiz.",
                "questions": ["Hangi isigi acmami istiyorsun? Oda veya cihaz adi belirt."],
                "target": "",
                "entities": {"device_name": "isik"},
            }
        if normalized_text == "sesi ayarla":
            return {
                "action_type": ActionType.PC_VOLUME_SET,
                "reason": "Ses seviyesi degeri eksik.",
                "questions": ["Ses seviyesini kacta ayarlamami istiyorsun?"],
                "target": "system volume",
                "entities": {},
            }
        return None

    def _match_conversation(self, normalized_text: str) -> dict[str, IntentCategory] | None:
        if "atlas su an ne durumda" in normalized_text or "sistem sagligi nasil" in normalized_text:
            return {"category": IntentCategory.CONVERSATION_STATUS}
        if "bugun ne yapmam gerekiyor" in normalized_text:
            return {"category": IntentCategory.CONVERSATION_QUESTION}
        return None

    def _match_system_info(self, normalized_text: str):
        if any(token in normalized_text for token in ("bilgisayar bilgilerini goster", "sistem bilgilerini goster", "bilgisayar bilgisi", "ram durumu", "diskte ne kadar yer var")):
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.PC_SYSTEM_INFO,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.94,
                entities={},
                target="system",
                action_type=ActionType.PC_SYSTEM_INFO,
                safety_notes=["Safe read-only system information request."],
            )
        return None

    def _match_volume(self, normalized_text: str):
        level_match = re.search(r"\b(?:ses seviyesini|sesi)\s+(\d{1,3})\s+yap\b", normalized_text)
        if level_match:
            level = max(0, min(100, int(level_match.group(1))))
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.PC_VOLUME_CONTROL,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.93,
                entities={"volume_level": level},
                target="system volume",
                action_type=ActionType.PC_VOLUME_SET,
            )
        if "sesi kapat" in normalized_text:
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.PC_VOLUME_CONTROL,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.93,
                entities={},
                target="system volume",
                action_type=ActionType.PC_VOLUME_MUTE_TOGGLE,
            )
        return None

    def _match_media(self, normalized_text: str):
        mapping = {
            "muzigi duraklat": ActionType.PC_MEDIA_PLAY_PAUSE,
            "sonraki sarkiya gec": ActionType.PC_MEDIA_NEXT,
            "onceki sarkiya don": ActionType.PC_MEDIA_PREVIOUS,
        }
        for token, action_type in mapping.items():
            if token in normalized_text:
                return lambda intent_id, raw_text, norm, token=token, action_type=action_type: self._intent(
                    intent_id=intent_id,
                    category=IntentCategory.PC_MEDIA_CONTROL,
                    raw_text=raw_text,
                    normalized_text=norm,
                    confidence=0.92,
                    entities={"media_command": token},
                    target="media",
                    action_type=action_type,
                )
        return None

    def _match_browser(self, normalized_text: str):
        google_match = re.search(r"google(?:da)?\s+(.+?)\s+ara\b", normalized_text)
        if google_match:
            query = google_match.group(1).strip()
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.BROWSER_SEARCH,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.92,
                entities={"query": query},
                target=query,
                action_type=ActionType.BROWSER_SEARCH,
            )
        youtube_match = re.search(r"youtube(?:da)?\s+(.+?)\s+ac\b", normalized_text)
        if youtube_match:
            query = youtube_match.group(1).strip()
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.BROWSER_SEARCH,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.9,
                entities={"query": query, "site": "youtube"},
                target=query,
                action_type=ActionType.BROWSER_SEARCH,
            )
        return None

    def _match_file_search(self, normalized_text: str):
        if "bul" not in normalized_text and "ara" not in normalized_text:
            return None
        if any(token in normalized_text for token in ("pdf dosyalarimi", "atlas dosyasini", "dosyalarimi", "dosyasini")):
            query = normalized_text.replace("bul", "").replace("ara", "").strip()
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.FILE_SEARCH,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.9,
                entities={"query": query},
                target=query or "file search",
                action_type=ActionType.FILE_SEARCH,
                safety_notes=["Safe read-only file search preview."],
            )
        return None

    def _match_reminder(self, normalized_text: str):
        later_match = re.search(r"bana\s+(.+?)\s+hatirlat", normalized_text)
        if later_match:
            fragment = later_match.group(1).strip()
            date_time_text = ""
            reminder_text = fragment
            after_match = re.match(r"(\d+\s+(?:dakika|saat)\s+sonra)\s+(.+)", fragment)
            if after_match:
                date_time_text = after_match.group(1)
                reminder_text = after_match.group(2)
            tomorrow_match = re.match(r"(yarin\s+\d{1,2}(?::\d{2})?(?:'da|da)?)\s+(.+)", fragment)
            if tomorrow_match:
                date_time_text = tomorrow_match.group(1)
                reminder_text = tomorrow_match.group(2)
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.REMINDER_CREATE,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.89,
                entities={"reminder_text": reminder_text.strip(), "date_time_text": date_time_text.strip()},
                target=reminder_text.strip() or "reminder",
                action_type=ActionType.REMINDER_CREATE,
            )
        if re.search(r"(yarin\s+\d{1,2}(?::\d{2})?(?:'da|da)?)\s+(.+?)\s+hatirlat", normalized_text):
            match = re.search(r"(yarin\s+\d{1,2}(?::\d{2})?(?:'da|da)?)\s+(.+?)\s+hatirlat", normalized_text)
            if match:
                return lambda intent_id, raw_text, norm: self._intent(
                    intent_id=intent_id,
                    category=IntentCategory.REMINDER_CREATE,
                    raw_text=raw_text,
                    normalized_text=norm,
                    confidence=0.9,
                    entities={"date_time_text": match.group(1), "reminder_text": match.group(2)},
                    target=match.group(2),
                    action_type=ActionType.REMINDER_CREATE,
                )
        return None

    def _match_routine(self, normalized_text: str):
        routine_name = self._match_alias(normalized_text, ROUTINE_ALIASES)
        if routine_name and any(token in normalized_text for token in ("baslat", "ac", "run")):
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.ROUTINE_RUN,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.92,
                entities={"routine_name": routine_name},
                target=routine_name,
                action_type=ActionType.ROUTINE_RUN_HIGH_IMPACT if routine_name == "evden cikiyorum" else ActionType.ROUTINE_RUN,
            )
        return None

    def _match_device(self, normalized_text: str):
        if "kamera" in normalized_text and re.search(r"\b(ac|izle|baslat)\b", normalized_text):
            return lambda intent_id, raw_text, norm: IntentResult(
                intent_id=intent_id,
                category=IntentCategory.BLOCKED,
                confidence=0.95,
                language="tr",
                raw_text=raw_text,
                normalized_text=norm,
                entities={"device_name": "kamera"},
                target="kamera",
                action_candidate=ActionType.DEVICE_DISABLE_SECURITY,
                safety_notes=["Kamera aksiyonlari privacy riski nedeniyle MVP'de blocked."],
            )
        if "kapi" in normalized_text and re.search(r"\b(ac|kilidi ac)\b", normalized_text):
            return lambda intent_id, raw_text, norm: IntentResult(
                intent_id=intent_id,
                category=IntentCategory.BLOCKED,
                confidence=0.95,
                language="tr",
                raw_text=raw_text,
                normalized_text=norm,
                entities={"device_name": "kapi"},
                target="kapi",
                action_candidate=ActionType.DEVICE_OPEN_DOOR,
                safety_notes=["Kapi veya kilit aksiyonlari fiziksel guvenlik nedeniyle MVP'de blocked."],
            )
        state_query_match = re.search(r"(acik mi|kapali mi|durumu ne|kac derece|durumunu goster)", normalized_text)
        if state_query_match:
            room_name = self._extract_room(normalized_text)
            device_name = self._extract_device(normalized_text)
            if "klima" in normalized_text or "termostat" in normalized_text:
                device_name = "klima"
            target = f"{room_name} {device_name}".strip() if device_name else (room_name or "device")
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.DEVICE_STATE_QUERY,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.88 if device_name else 0.72,
                entities={"room_name": room_name, "device_name": device_name, "query_type": "state"},
                target=target,
                action_type=ActionType.DEVICE_STATE_QUERY,
                safety_notes=["Safe read-only device state query."],
            )
        temperature_match = re.search(r"(klimayi|termostatini|klima|termostat)\s+(\d{1,2})\s+derece\s+yap", normalized_text)
        if temperature_match:
            room_name = self._extract_room(normalized_text)
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.DEVICE_SET_TEMPERATURE,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.9,
                entities={"device_name": temperature_match.group(1), "temperature": int(temperature_match.group(2)), "room_name": room_name},
                target=room_name or "klima",
                action_type=ActionType.DEVICE_SET_TEMPERATURE,
            )
        brightness_match = re.search(r"(.+?)\s+(?:yuzde\s+)?(\d{1,3})\s+yap", normalized_text)
        if brightness_match and ("isik" in normalized_text or "isig" in normalized_text or "lamba" in normalized_text):
            room_name = self._extract_room(normalized_text)
            brightness = max(0, min(100, int(brightness_match.group(2))))
            target = f"{room_name} isik".strip() if room_name else "isik"
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.DEVICE_SET_BRIGHTNESS,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.9 if room_name else 0.72,
                entities={"room_name": room_name, "device_name": "isik", "brightness": brightness},
                target=target,
                action_type=ActionType.DEVICE_SET_BRIGHTNESS,
            )
        device_name = self._extract_device(normalized_text)
        room_name = self._extract_room(normalized_text)
        if device_name and not room_name and "ana isik" in normalized_text and re.search(r"\bac\b", normalized_text):
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.DEVICE_TURN_ON,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.84,
                entities={"device_name": "ana isik"},
                target="ana isik",
                action_type=ActionType.DEVICE_TURN_ON,
            )
        if device_name and not room_name and "ana isik" in normalized_text and "kapat" in normalized_text:
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.DEVICE_TURN_OFF,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.84,
                entities={"device_name": "ana isik"},
                target="ana isik",
                action_type=ActionType.DEVICE_TURN_OFF,
            )
        if device_name and room_name and re.search(r"\bac\b", normalized_text):
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.DEVICE_TURN_ON,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.91,
                entities={"room_name": room_name, "device_name": device_name},
                target=f"{room_name} {device_name}",
                action_type=ActionType.DEVICE_TURN_ON,
            )
        if device_name and room_name and "kapat" in normalized_text:
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.DEVICE_TURN_OFF,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.91,
                entities={"room_name": room_name, "device_name": device_name},
                target=f"{room_name} {device_name}",
                action_type=ActionType.DEVICE_TURN_OFF,
            )
        if device_name and not room_name and re.search(r"\bac\b", normalized_text):
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.DEVICE_TURN_ON,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.74,
                entities={"device_name": device_name},
                target=device_name,
                action_type=ActionType.DEVICE_TURN_ON,
            )
        if device_name and not room_name and "kapat" in normalized_text:
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.DEVICE_TURN_OFF,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.74,
                entities={"device_name": device_name},
                target=device_name,
                action_type=ActionType.DEVICE_TURN_OFF,
            )
        return None

    def _match_power_action(self, normalized_text: str):
        if "bilgisayari kapat" in normalized_text:
            return lambda intent_id, raw_text, norm: self._intent(
                intent_id=intent_id,
                category=IntentCategory.CONVERSATION_STATUS,
                raw_text=raw_text,
                normalized_text=norm,
                confidence=0.93,
                entities={},
                target="bilgisayar",
                action_type=ActionType.PC_SHUTDOWN,
                safety_notes=["High-risk power action; confirmation required."],
            )
        return None

    def _clarification_from_intent(self, intent: IntentResult) -> ClarificationRequest | None:
        if not intent.requires_clarification:
            return None
        return ClarificationRequest(
            reason=intent.ambiguity_reason or "Clarification required.",
            missing_fields=self._missing_fields(intent, None),
            candidate_targets=self._candidate_targets(intent),
            suggested_questions=intent.suggested_questions or ["Komutu daha net tarif eder misin?"],
        )

    def _missing_fields(self, intent: IntentResult, action: ActionCandidate | None) -> list[str]:
        missing: list[str] = []
        if intent.category is IntentCategory.AMBIGUOUS:
            if "room_name" not in intent.entities and intent.action_candidate in {ActionType.DEVICE_TURN_ON, ActionType.DEVICE_TURN_OFF}:
                missing.append("room_name")
            if action is not None and not action.target.strip():
                missing.append("target")
            if intent.action_candidate is ActionType.PC_VOLUME_SET and "volume_level" not in intent.entities:
                missing.append("volume_level")
        if intent.category is IntentCategory.UNKNOWN:
            missing.append("intent")
        return missing

    def _candidate_targets(self, intent: IntentResult) -> list[str]:
        if intent.action_candidate in {ActionType.DEVICE_TURN_ON, ActionType.DEVICE_TURN_OFF}:
            return list(ROOM_ALIASES)
        if intent.action_candidate is ActionType.ROUTINE_RUN:
            return list(ROUTINE_ALIASES.values())
        if intent.action_candidate is ActionType.PC_VOLUME_SET:
            return ["10", "20", "30", "50"]
        return []

    def _expected_result(self, action_type: ActionType, target: str, parameters: dict[str, object]) -> str:
        mapping = {
            ActionType.PC_OPEN_APP: f"{target} acilir.",
            ActionType.PC_OPEN_FOLDER: f"{target} klasoru preview edilir.",
            ActionType.PC_SYSTEM_INFO: "Sistem bilgileri gosterilir.",
            ActionType.FILE_SEARCH: "Dosya arama sonucu preview edilir.",
            ActionType.BROWSER_SEARCH: f"{target} icin tarayici arama preview edilir.",
            ActionType.REMINDER_CREATE: "Hatirlatici olusturma preview edilir.",
            ActionType.ROUTINE_RUN: f"{target} rutini preview edilir.",
            ActionType.ROUTINE_RUN_HIGH_IMPACT: f"{target} rutini yuksek etkili preview olarak gosterilir.",
            ActionType.DEVICE_TURN_ON: f"{target} acma action'i preview edilir.",
            ActionType.DEVICE_TURN_OFF: f"{target} kapatma action'i preview edilir.",
            ActionType.DEVICE_SET_TEMPERATURE: f"{target} sicakligi {parameters.get('temperature', '')} dereceye ayarlama preview edilir.",
            ActionType.PC_SHUTDOWN: "Bilgisayari kapatma action'i preview edilir.",
            ActionType.PC_VOLUME_SET: f"Ses seviyesi {parameters.get('volume_level', '')} olarak preview edilir.",
            ActionType.PC_VOLUME_MUTE_TOGGLE: "Sesi kapatma/acma preview edilir.",
            ActionType.PC_MEDIA_PLAY_PAUSE: "Muzik duraklat/devam preview edilir.",
            ActionType.PC_MEDIA_NEXT: "Sonraki medya oge preview edilir.",
            ActionType.PC_MEDIA_PREVIOUS: "Onceki medya oge preview edilir.",
        }
        return mapping.get(action_type, f"{action_type.value} preview edilir.")

    def _contains_open_verb(self, normalized_text: str) -> bool:
        return bool(re.search(r"\b(ac|baslat|goster)\b", normalized_text))

    def _blocked_target(self, normalized_text: str) -> str:
        if "dosya" in normalized_text:
            return "dosya"
        if "registry" in normalized_text:
            return "registry"
        if "sifre" in normalized_text:
            return "secret"
        if "disk" in normalized_text:
            return "disk"
        return "blocked-target"

    def _match_alias(self, normalized_text: str, aliases: dict[str, str]) -> str | None:
        for key, value in aliases.items():
            if key in normalized_text:
                return value
        return None

    def _extract_room(self, normalized_text: str) -> str:
        for room in ROOM_ALIASES:
            if room in normalized_text:
                return room
        return ""

    def _extract_device(self, normalized_text: str) -> str:
        if "isig" in normalized_text or "isik" in normalized_text:
            return "isik"
        for device in DEVICE_ALIASES:
            if device in normalized_text:
                return device
        return ""

    def _normalize(self, text: str) -> str:
        normalized = text.strip().lower()
        normalized = normalized.replace("’", "'").replace("`", "'")
        normalized = normalized.translate(
            str.maketrans(
                {
                    "ç": "c",
                    "ğ": "g",
                    "ı": "i",
                    "ö": "o",
                    "ş": "s",
                    "ü": "u",
                }
            )
        )
        normalized = re.sub(r"['\"]", "", normalized)
        normalized = re.sub(r"[!?.,:()]+", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized
