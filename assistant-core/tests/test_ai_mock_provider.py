from __future__ import annotations

from app.ai.models import AIContextBundle, AIContextSource
from app.ai.providers.mock_provider import MockAIProvider


def test_mock_provider_generates_response() -> None:
    provider = MockAIProvider()
    bundle = AIContextBundle(
        project="ATLAS",
        sources=[AIContextSource(kind="knowledge-base", label="03-current-status.md", path="x", content="status")],
    )
    response = provider.generate(prompt="ATLAS su an ne durumda?", context=bundle)
    assert response.provider == "mock"
    assert "MOCK PROVIDER" in response.text
    assert "03-current-status.md" in response.text
