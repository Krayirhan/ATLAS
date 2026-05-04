from __future__ import annotations

from app.ai.models import AIContextBundle, AIContextSource
from app.ai.prompt_composer import PromptComposer


def test_prompt_composer_includes_safety_rules() -> None:
    composer = PromptComposer()
    bundle = AIContextBundle(
        project="ATLAS",
        sources=[
            AIContextSource(kind="knowledge-base", label="03-current-status.md", path="E:/ATLAS/x.md", content="status")
        ],
    )
    prompt = composer.compose(project="ATLAS", question="Durum ne?", context=bundle)
    assert "read-only advisory mode" in prompt
    assert "Do not instruct file writes" in prompt
    assert "Varsayilan yanit dili Turkce olsun." in prompt
    assert "Durum ne?" in prompt
