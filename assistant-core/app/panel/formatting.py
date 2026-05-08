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
        f"Item ID: {item.item_id}",
        f"Type: {item.item_type.value}",
        f"Status: {item.status.value}",
        f"Title: {item.title}",
        f"Summary: {item.summary}",
        f"Risk: {risk_badge(item.risk_level)}",
        f"Source: {item.source}",
        f"Target: {item.target or '-'}",
        f"Requires Confirmation: {item.requires_confirmation}",
    ]
    if item.confirmation_prompt:
        lines.append(f"Confirmation Prompt: {item.confirmation_prompt}")
    if item.blocked_reason:
        lines.append(f"Blocked Reason: {item.blocked_reason}")
    if item.clarification_prompt:
        lines.append(f"Clarification: {item.clarification_prompt}")
    if item.warnings:
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in item.warnings)
    lines.append("Note: Bu sadece onizlemedir, islem calistirilmadi.")
    return "\n".join(lines)


def format_items_table(items: list[PermissionPanelItem]) -> str:
    if not items:
        return "Panel bos."
    lines = ["ID | Type | Status | Risk | Summary"]
    for item in items:
        lines.append(
            f"{item.item_id} | {item.item_type.value} | {item.status.value} | "
            f"{risk_badge(item.risk_level)} | {item.summary}"
        )
    lines.append("Not: Bu sadece onizlemedir, islem calistirilmadi.")
    return "\n".join(lines)


def format_operation(result: PanelOperationResult) -> str:
    lines = [f"Status: {result.status.value}", f"Message: {result.message}"]
    if result.item is not None:
        lines.append(format_item_detail(result.item))
    elif result.items:
        lines.append(format_items_table(result.items))
    return "\n".join(lines)
