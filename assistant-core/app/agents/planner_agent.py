"""PlannerAgent: produce bounded read-only implementation plans."""

from __future__ import annotations

from pathlib import Path

from app.agents.base import BaseAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.models import (
    AgentContextSource,
    AgentRunRequest,
    AgentRunResult,
    PlanAcceptanceCriterion,
    PlannedFileImpact,
    PlannerRequest,
    PlannerResult,
    PlanRisk,
    PlanTestStep,
    SprintPlan,
)
from app.ai.context_loader import AIContextError
from app.ai.models import AIContextBundle, AIContextSource
from app.ai.providers.base import AIProviderError
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.providers.ollama_provider import OllamaAIProvider
from app.config.loader import load_assistant_settings
from app.logging.audit import write_audit
from app.paths import get_atlas_root, get_logs_dir, get_workspace_dir


class PlannerAgent(BaseAgent):
    agent_name = "planner-agent"

    def __init__(self, *, memory_agent: MemoryAgent | None = None) -> None:
        self._settings = load_assistant_settings()
        self._memory_agent = memory_agent or MemoryAgent()

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        result = self.plan(PlannerRequest(project_name=request.project_name, goal=request.question, provider=request.provider))
        return AgentRunResult(
            agent_name=result.agent_name,
            project_name=result.project_name,
            status=result.status,
            answer=result.plan_summary,
            sources=result.sources,
            warnings=result.warnings,
            metadata=result.metadata,
        )

    def plan(self, request: PlannerRequest) -> PlannerResult:
        snapshot = self._memory_agent.snapshot(request.project_name)
        provider_name = (request.provider or self._settings.ai.default_provider).strip().lower()
        warnings = list(snapshot.warnings)
        assumptions = [
            "Bu sprint sadece plan uretir; uygulama ayri onay gerektirir.",
            "Read-only sinir korunur; dosya degisikligi veya komut calistirma yoktur.",
        ]
        out_of_scope = [
            "Kod yazmak veya patch uygulamak",
            "Terminal komutu calistirmak",
            "Git islemleri yapmak",
            "MCP tool cagrisi yapmak",
        ]

        sources = list(snapshot.context_sources)
        extra_sources = self._planner_sources()
        sources.extend(extra_sources)

        plan = self._deterministic_plan(request.goal, request.max_sprints)
        plan_summary = self._format_summary(plan, provider_name)
        status = "ok"
        metadata = {
            "provider": provider_name,
            "source_count": len(sources),
        }

        if provider_name == "ollama":
            try:
                answer = self._ollama_plan_summary(request.goal, snapshot, sources)
                if answer:
                    plan_summary = answer
            except AIProviderError as exc:
                warnings.append(str(exc))
                status = "warning"
        elif provider_name == "mock":
            plan_summary = "Read-only plan mode.\n\n" + plan_summary
        else:
            raise AIProviderError(f"Unknown AI provider: {provider_name}")

        write_audit(
            event="agent_planner_run",
            payload={
                "agent_name": self.agent_name,
                "provider": provider_name,
                "project": request.project_name,
                "source_count": len(sources),
            },
            logs_root=get_logs_dir(),
            stream="tool-calls",
        )
        return PlannerResult(
            agent_name=self.agent_name,
            project_name=request.project_name,
            goal=request.goal,
            status=status,
            plan_summary=plan_summary,
            proposed_sprints=plan,
            risks=plan[0].risks if plan else [],
            assumptions=assumptions,
            out_of_scope=out_of_scope,
            sources=sources,
            warnings=warnings,
            metadata=metadata,
        )

    def _deterministic_plan(self, goal: str, max_sprints: int) -> list[SprintPlan]:
        sprint_name = "Sprint 30 Plan"
        scope = [
            f"Hedefi daralt: {goal}",
            "MemoryAgent ve mevcut KB durumunu baz alarak teslim parcaciklarini netlestir",
            "Uygulama oncesi acceptance criteria ve test planini kesinlestir",
        ]
        expected_files = [
            PlannedFileImpact(path="assistant-core/app/agents/<target>.py", reason="Hedef ozelligi icin agent veya destek modulu"),
            PlannedFileImpact(path="assistant-core/tests/test_<target>.py", reason="Riske orantili test kapsamasi"),
            PlannedFileImpact(path="workspace/knowledge-base/ATLAS/*.md", reason="Sprint sonucu ve plan dokumantasyonu"),
        ]
        risks = [
            PlanRisk(title="Scope drift", detail="Hedef bir sprint icin fazla genisse PlannerAgent once parcaliyormus gibi davranmali."),
            PlanRisk(title="Read-only boundary", detail="Plan ile uygulama birbirine karismamali; bu sprintte sadece plan uretilmeli."),
            PlanRisk(title="Provider/runtime", detail="Ollama sagligi dusukse mock uzerinden plan akisi yine calismali."),
        ]
        acceptance = [
            PlanAcceptanceCriterion(text="Objective, scope, out_of_scope, risks, acceptance criteria ve test plani acik yazilmis olmali."),
            PlanAcceptanceCriterion(text="Uygulama icin acik kullanici onayi gerektigi belirtilmeli."),
            PlanAcceptanceCriterion(text="Read-only sinirlar bozulmamis olmali."),
        ]
        tests = [
            PlanTestStep(text="Yeni sprint hedefi icin unit testler ve CLI smoke testleri belirlenmeli."),
            PlanTestStep(text="Pre-flight ve final validation komutlari plan icinde tekrar edilmeli."),
        ]
        validation = [
            "python -m pytest -q",
            "python -m app.cli doctor --full",
            "python -m app.cli config validate",
            "python -m app.cli project validate ATLAS",
        ]
        return [
            SprintPlan(
                sprint_name=sprint_name,
                objective=goal,
                scope=scope,
                out_of_scope=[
                    "Kod uygulamasi yapmak",
                    "Terminal/git/MCP islemleri",
                ],
                expected_files=expected_files,
                risks=risks,
                acceptance_criteria=acceptance,
                test_plan=tests,
                validation_commands=validation,
                next_dependency="Sprint 31 - CodeReviewerAgent Alpha",
            )
        ][: max(1, max_sprints)]

    def _planner_sources(self) -> list[AgentContextSource]:
        kb = get_workspace_dir() / "knowledge-base" / "ATLAS"
        names = [
            "06-next-sprints.md",
            "04-risk-list.md",
            "07-v1-rc-go-report.md",
            "14-sprint-29-memory-agent-projectqa-plan.md",
            "13-sprint-28-ai-layer-foundation-plan.md",
        ]
        sources: list[AgentContextSource] = []
        for name in names:
            path = kb / name
            if path.is_file():
                sources.append(
                    AgentContextSource(
                        source_type="knowledge-base",
                        label=name,
                        path=str(path.resolve()),
                        char_count=min(len(path.read_text(encoding="utf-8", errors="replace")), 4000),
                        metadata={},
                    )
                )
        return sources

    def _ollama_plan_summary(self, goal: str, snapshot, sources: list[AgentContextSource]) -> str:
        provider = OllamaAIProvider(self._settings.ai.ollama)
        health = provider.health_check()
        if not health.ok:
            raise AIProviderError(health.message)
        bundle = AIContextBundle(
            project=snapshot.project_name,
            sources=[
                AIContextSource(
                    kind="planner",
                    label="planner-memory",
                    path=snapshot.knowledge_path,
                    content=(
                        "You are PlannerAgent in read-only advisory mode.\n"
                        "Do not claim you changed files.\n"
                        "Do not claim you ran commands.\n"
                        "Produce a bounded implementation plan only.\n"
                        "Mention risks and acceptance criteria.\n"
                        "Ask for explicit approval before any implementation.\n\n"
                        f"Current status:\n{snapshot.current_status}\n\n"
                        f"Risks:\n{snapshot.risks}\n\n"
                        f"Next sprints:\n{snapshot.next_sprints}\n\n"
                        f"Release status:\n{snapshot.release_status}\n"
                    ),
                    metadata={},
                )
            ],
            metadata={"total_chars": len(snapshot.current_status) + len(snapshot.risks), "max_total_chars": 12000},
        )
        prompt = (
            "You are PlannerAgent in read-only advisory mode.\n"
            "Do not claim you changed files.\n"
            "Do not claim you ran commands.\n"
            "Produce a bounded implementation plan only.\n"
            "Mention risks and acceptance criteria.\n"
            "Ask for explicit approval before any implementation.\n"
            "Yaniti Turkce ver.\n\n"
            f"Kullanici hedefi: {goal}\n"
            "Cikti kisa ve uygulanabilir olsun."
        )
        return provider.generate(prompt=prompt, context=bundle).text

    def _format_summary(self, plans: list[SprintPlan], provider_name: str) -> str:
        plan = plans[0]
        lines = [
            f"Provider: {provider_name}",
            f"Sprint: {plan.sprint_name}",
            f"Objective: {plan.objective}",
            "",
            "Scope:",
            *[f"- {item}" for item in plan.scope],
            "",
            "Out of scope:",
            *[f"- {item}" for item in plan.out_of_scope],
            "",
            "Risks:",
            *[f"- {risk.title}: {risk.detail}" for risk in plan.risks],
            "",
            "Acceptance criteria:",
            *[f"- {item.text}" for item in plan.acceptance_criteria],
            "",
            "Test plan:",
            *[f"- {item.text}" for item in plan.test_plan],
            "",
            "Explicit approval is required before implementation.",
        ]
        return "\n".join(lines)
