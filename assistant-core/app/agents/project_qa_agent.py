"""ProjectQAAgent: answer project questions from a read-only snapshot."""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.models import (
    AgentContextSource,
    AgentRunRequest,
    AgentRunResult,
    ProjectQARequest,
    ProjectQAResult,
)
from app.ai.models import AIContextBundle, AIContextSource
from app.ai.prompt_composer import PromptComposer
from app.ai.providers.base import AIProviderError
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.providers.ollama_provider import OllamaAIProvider
from app.config.loader import load_assistant_settings
from app.logging.audit import write_audit
from app.paths import get_logs_dir


class ProjectQAAgent(BaseAgent):
    agent_name = "project-qa-agent"

    def __init__(
        self,
        *,
        memory_agent: MemoryAgent | None = None,
        prompt_composer: PromptComposer | None = None,
    ) -> None:
        self._settings = load_assistant_settings()
        self._memory_agent = memory_agent or MemoryAgent()
        self._prompt_composer = prompt_composer or PromptComposer()

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        result = self.answer(
            ProjectQARequest(
                project_name=request.project_name,
                question=request.question,
                provider=request.provider,
                show_sources=request.show_sources,
                show_context=request.show_context,
            )
        )
        return AgentRunResult(
            agent_name=result.agent_name,
            project_name=result.project_name,
            status=result.status,
            answer=result.answer,
            sources=result.sources,
            warnings=result.warnings,
            metadata=result.metadata,
        )

    def answer(self, request: ProjectQARequest) -> ProjectQAResult:
        snapshot = self._memory_agent.snapshot(request.project_name)
        provider_name = (request.provider or self._settings.ai.default_provider).strip().lower()
        provider = self._provider(provider_name)
        if provider_name == "ollama":
            health = provider.health_check()
            if not health.ok:
                raise AIProviderError(health.message)
        bundle = self._to_context_bundle(snapshot)
        prompt = self._prompt_composer.compose(project=request.project_name, question=request.question, context=bundle)

        warnings = list(snapshot.warnings)
        status = "ok"
        try:
            response = provider.generate(prompt=prompt, context=bundle)
            answer = response.text
            if provider_name == "mock":
                answer = "Read-only advisory mode.\n\n" + answer
            metadata = {
                "provider": provider_name,
                "source_count": len(snapshot.context_sources),
                "context_total_chars": bundle.metadata.get("total_chars", 0),
                "context_limit_chars": bundle.metadata.get("max_total_chars", 0),
            }
            metadata.update(response.metadata)
        except AIProviderError as exc:
            answer = (
                "Ollama yaniti alinamadi. Runtime hazir olmayabilir veya model timeout oldu. "
                "Read-only sinir korunuyor; hicbir dosya veya komut calistirilmayacak.\n\n"
                f"Detay: {exc}"
            )
            warnings.append(str(exc))
            status = "warning"
            metadata = {
                "provider": provider_name,
                "source_count": len(snapshot.context_sources),
                "context_total_chars": bundle.metadata.get("total_chars", 0),
                "context_limit_chars": bundle.metadata.get("max_total_chars", 0),
            }

        write_audit(
            event="agent_project_qa_run",
            payload={
                "agent_name": self.agent_name,
                "provider": provider_name,
                "project": request.project_name,
                "source_count": len(snapshot.context_sources),
            },
            logs_root=get_logs_dir(),
            stream="tool-calls",
        )
        return ProjectQAResult(
            agent_name=self.agent_name,
            project_name=request.project_name,
            status=status,
            answer=answer,
            sources=snapshot.context_sources,
            warnings=warnings,
            metadata=metadata,
        )

    def _provider(self, provider_name: str):
        if provider_name == "mock":
            return MockAIProvider()
        if provider_name == "ollama":
            return OllamaAIProvider(self._settings.ai.ollama)
        raise AIProviderError(f"Unknown AI provider: {provider_name}")

    def _to_context_bundle(self, snapshot) -> AIContextBundle:
        sources = [
            AIContextSource(
                kind=source.source_type,
                label=source.label,
                path=source.path,
                content=f"{source.label} ({source.char_count} chars)",
                metadata=dict(source.metadata),
            )
            for source in snapshot.context_sources
        ]
        # richer content for actual answer generation
        rich_sources: list[AIContextSource] = []
        rich_sources.append(
            AIContextSource(
                kind="memory",
                label="memory-snapshot",
                path=snapshot.knowledge_path,
                content=self._limit_text(
                    (
                    f"project_name: {snapshot.project_name}\n"
                    f"project_type: {snapshot.project_type}\n"
                    f"current_status:\n{snapshot.current_status}\n\n"
                    f"risks:\n{snapshot.risks}\n\n"
                    f"next_sprints:\n{snapshot.next_sprints}\n\n"
                    f"release_status:\n{snapshot.release_status}\n"
                    ),
                    8000,
                ),
                metadata={"char_count": len(snapshot.current_status) + len(snapshot.risks) + len(snapshot.next_sprints)},
            )
        )
        rich_sources.extend(
            AIContextSource(
                kind=src.source_type,
                label=src.label,
                path=src.path,
                content=f"path: {src.path}\nchar_count: {src.char_count}",
                metadata=dict(src.metadata),
            )
            for src in snapshot.context_sources
            if src.source_type in {"registry", "report"}
        )
        total_chars = sum(len(item.content) for item in rich_sources)
        return AIContextBundle(
            project=snapshot.project_name,
            sources=rich_sources if rich_sources else sources,
            metadata={"total_chars": total_chars, "max_total_chars": 12000},
        )

    def _limit_text(self, text: str, limit: int) -> str:
        if len(text) <= limit:
            return text
        suffix = "\n...[truncated]..."
        return text[: limit - len(suffix)] + suffix
