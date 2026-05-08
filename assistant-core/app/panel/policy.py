from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.panel.models import PanelItemStatus, PanelItemType, PermissionPanelItem

DEFAULT_EXPIRY_MINUTES = 30
MAX_STORED_ITEMS = 200
MAX_STRING_LENGTH = 500
REDACTION_TOKENS = ("password", "token", "secret", "api_key", "credential")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def default_expiry() -> datetime:
    return utcnow() + timedelta(minutes=DEFAULT_EXPIRY_MINUTES)


def is_expired(item: PermissionPanelItem) -> bool:
    return item.expires_at is not None and item.expires_at <= utcnow()


def sanitize_text(text: str) -> str:
    value = " ".join(text.strip().split())
    lowered = value.lower()
    if any(token in lowered for token in REDACTION_TOKENS):
        return "[redacted-sensitive-text]"
    if len(value) > MAX_STRING_LENGTH:
        return value[:MAX_STRING_LENGTH] + "..."
    return value


def sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, list):
        return [sanitize_value(item) for item in value][:50]
    if isinstance(value, dict):
        safe: dict[str, Any] = {}
        for key, item in list(value.items())[:100]:
            if any(token in key.lower() for token in REDACTION_TOKENS):
                safe[key] = "[redacted]"
            else:
                safe[key] = sanitize_value(item)
        return safe
    return value


def can_approve(item: PermissionPanelItem) -> tuple[bool, str]:
    if is_expired(item) or item.status is PanelItemStatus.EXPIRED:
        return False, "Bu panel ogesi zaman asimina ugradi."
    if item.item_type is PanelItemType.BLOCKED or item.status is PanelItemStatus.BLOCKED:
        return False, "Blocked panel ogesi approve edilemez."
    if item.item_type is PanelItemType.CLARIFICATION_REQUIRED:
        return False, "Clarification gereken panel ogesi approve edilemez."
    if item.status in {PanelItemStatus.DENIED, PanelItemStatus.CANCELLED, PanelItemStatus.RESOLVED}:
        return False, "Bu panel ogesi artik bekleyen durumda degil."
    return True, ""


def ensure_status(item: PermissionPanelItem) -> PermissionPanelItem:
    if is_expired(item):
        item.status = PanelItemStatus.EXPIRED
    return item
