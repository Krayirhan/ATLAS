"""Compose bounded prompts for the read-only AI layer."""

from __future__ import annotations

from app.ai.models import AIContextBundle


class PromptComposer:
    def compose(self, *, project: str, question: str, context: AIContextBundle) -> str:
        sections = [
            "You are ATLAS AI Assistant running in read-only advisory mode.",
            "",
            "Safety rules:",
            "- Do not instruct file writes, shell execution, git actions, tool calls, or agent orchestration.",
            "- Use only the supplied ATLAS context.",
            "- Never claim hidden access to secrets, .env files, or unrestricted repo scans.",
            "- Varsayilan yanit dili Turkce olsun.",
            "",
            "Project identity:",
            f"- Project: {project}",
            "",
        ]
        for source in context.sources:
            sections.append(f"[{source.kind}] {source.label} | {source.path}")
            sections.append(source.content.strip())
            sections.append("")
        sections.extend(
            [
                "User question:",
                question.strip(),
            ]
        )
        return "\n".join(sections).strip() + "\n"
