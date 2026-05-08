from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.panel.models import ConfirmationTimeoutPolicy, PanelItemStatus, PanelItemType, PermissionPanelItem

DEFAULT_EXPIRY_MINUTES = 30
DEFAULT_TIMEOUT_SECONDS = DEFAULT_EXPIRY_MINUTES * 60
MAX_STORED_ITEMS = 200
MAX_STRING_LENGTH = 500
REDACTION_TOKENS = ("password", "token", "secret", "api_key", "credential")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def default_expiry() -> datetime:
    return utcnow() + timedelta(minutes=DEFAULT_EXPIRY_MINUTES)


def build_timeout_policy(*, default_timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> ConfirmationTimeoutPolicy:
    return ConfirmationTimeoutPolicy(
        default_timeout_seconds=default_timeout_seconds,
        expires_at=utcnow() + timedelta(seconds=default_timeout_seconds),
    )


def is_expired(item: PermissionPanelItem) -> bool:
    expires_at = item.expires_at
    if expires_at is None and item.timeout_policy is not None:
        expires_at = item.timeout_policy.expires_at
    return expires_at is not None and expires_at <= utcnow()


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
        return False, "Bu panel öğesinin onay süresi doldu; artık approve edilemez."
    if item.item_type is PanelItemType.APPROVED_PREVIEW or item.status is PanelItemStatus.APPROVED:
        return False, "Bu panel öğesi zaten approved_preview durumunda; gerçek işlem başlatılamaz."
    if item.item_type is PanelItemType.BLOCKED or item.status is PanelItemStatus.BLOCKED:
        return False, "Engellenen panel öğesi approve edilemez."
    if item.item_type is PanelItemType.CLARIFICATION_REQUIRED:
        return False, "Belirsiz hedef veya ek açıklama gereken panel öğesi approve edilemez."
    if item.status is PanelItemStatus.DENIED:
        return False, "Reddedilen panel öğesi tekrar approve edilemez."
    if item.status is PanelItemStatus.CANCELLED:
        return False, "İptal edilen panel öğesi tekrar approve edilemez."
    if item.status is PanelItemStatus.RESOLVED:
        return False, "Bu panel öğesi artık bekleyen durumda değil."
    return True, ""


def ensure_status(item: PermissionPanelItem) -> PermissionPanelItem:
    if is_expired(item):
        item.status = PanelItemStatus.EXPIRED
    if item.timeout_policy is not None:
        item.expires_at = item.timeout_policy.expires_at
    return item
