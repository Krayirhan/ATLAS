from __future__ import annotations

from app.panel.models import PanelOperationResult, PermissionPanelItem


def risk_badge(risk_level: str) -> str:
    mapping = {
        "safe_readonly": "SAFE_READONLY",
        "low": "LOW",
        "medium": "MEDIUM",
        "high": "HIGH",
        "blocked": "BLOCKED",
    }
    return mapping.get(risk_level, risk_level.upper() if risk_level else "UNKNOWN")


def format_item_detail(item: PermissionPanelItem) -> str:
    lines = [
        f"Oge ID: {item.item_id}",
        f"Tur: {item.item_type.value}",
        f"Durum: {item.status.value}",
        f"Baslik: {item.title}",
        f"Ozet: {item.summary}",
        f"Risk: {risk_badge(item.risk_level)}",
        f"Kaynak: {item.source}",
        f"Hedef: {item.target or '-'}",
        f"Onay gerekiyor: {item.requires_confirmation}",
    ]
    if item.confirmation_prompt:
        lines.append(f"Onay metni: {item.confirmation_prompt}")
    if item.blocked_reason:
        lines.append(f"Engel nedeni: {item.blocked_reason}")
    if item.clarification_prompt:
        lines.append(f"Belirsiz hedef: {item.clarification_prompt}")
    if item.warnings:
        lines.append("Uyarilar:")
        lines.extend(f"- {warning}" for warning in item.warnings)
    if item.timeout_policy is not None:
        lines.append(f"Onay zaman asimi: {item.timeout_policy.expires_at.isoformat()}")
    lines.append("Not: Bu sadece önizlemedir; gerçek işlem yapılmadı.")
    return "\n".join(lines)


def format_items_table(items: list[PermissionPanelItem]) -> str:
    if not items:
        return "Panel boş."
    lines = ["ID | Tur | Durum | Risk | Ozet"]
    for item in items:
        lines.append(
            f"{item.item_id} | {item.item_type.value} | {item.status.value} | "
            f"{risk_badge(item.risk_level)} | {item.summary}"
        )
    lines.append("Not: Bu sadece önizlemedir; gerçek işlem yapılmadı.")
    return "\n".join(lines)


def format_operation(result: PanelOperationResult) -> str:
    lines = [f"Durum: {result.status.value}", f"Mesaj: {result.message}"]
    if result.item is not None:
        lines.append(format_item_detail(result.item))
    elif result.items:
        lines.append(format_items_table(result.items))
    return "\n".join(lines)
