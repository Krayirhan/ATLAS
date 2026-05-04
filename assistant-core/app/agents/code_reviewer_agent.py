"""CodeReviewerAgent: bounded read-only review over approved project files."""

from __future__ import annotations

from pathlib import Path

from app.agents.base import BaseAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.models import (
    AgentContextSource,
    AgentRunRequest,
    AgentRunResult,
    CodeReviewFinding,
    CodeReviewRequest,
    CodeReviewResult,
    ReviewRecommendation,
    ReviewTestSuggestion,
)
from app.ai.context_loader import AIContextError
from app.ai.models import AIContextBundle, AIContextSource
from app.ai.providers.base import AIProviderError
from app.ai.providers.ollama_provider import OllamaAIProvider
from app.config.loader import load_assistant_settings
from app.logging.audit import write_audit
from app.paths import get_atlas_root, get_logs_dir


class CodeReviewerAgent(BaseAgent):
    agent_name = "code-reviewer-agent"
    _MAX_TOTAL_CONTEXT_CHARS = 12000
    _SCOPE_PATTERNS = {
        "safety": [
            "configs/safety-policy.json",
            "assistant-core/app/safety/*.py",
            "assistant-core/app/commands/command.py",
            "assistant-core/app/commands/ai.py",
            "workspace/knowledge-base/ATLAS/15-ai-security-boundaries.md",
        ],
        "ai-layer": [
            "assistant-core/app/ai/**/*.py",
            "assistant-core/app/agents/**/*.py",
            "assistant-core/tests/test_ai_*.py",
            "assistant-core/tests/test_*agent*.py",
        ],
        "config": [
            "configs/assistant.settings.json",
            "configs/project-registry.json",
            "configs/mcp.master.json",
            "assistant-core/app/config/**/*.py",
        ],
        "mcp": [
            "configs/mcp.master.json",
            "configs/generated/**/*",
            "assistant-core/app/mcp/**/*.py",
            "mcp-servers/**/*",
        ],
        "tests": [
            "assistant-core/tests/**/*.py",
        ],
        "docs": [
            "assistant-core/README.md",
            "workspace/knowledge-base/ATLAS/*.md",
        ],
        "architecture": [
            "assistant-core/app/**/*.py",
            "assistant-core/README.md",
            "workspace/knowledge-base/ATLAS/08-ai-layer-design.md",
            "workspace/knowledge-base/ATLAS/11-ai-context-contract.md",
        ],
        "all-light": [
            "assistant-core/README.md",
            "configs/*.json",
            "workspace/knowledge-base/ATLAS/00-project-summary.md",
            "workspace/knowledge-base/ATLAS/03-current-status.md",
            "workspace/knowledge-base/ATLAS/04-risk-list.md",
            "workspace/knowledge-base/ATLAS/06-next-sprints.md",
            "workspace/knowledge-base/ATLAS/07-v1-rc-go-report.md",
            "workspace/knowledge-base/ATLAS/15-ai-security-boundaries.md",
        ],
    }
    _BLOCKED_NAMES = {".env", ".env.local", "id_rsa", "id_ed25519", "known_hosts"}
    _BLOCKED_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".kdbx"}
    _BLOCKED_PATH_TOKENS = {"d:\\atlas"}

    def __init__(self, *, memory_agent: MemoryAgent | None = None) -> None:
        self._settings = load_assistant_settings()
        self._memory_agent = memory_agent or MemoryAgent()

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        result = self.review(
            CodeReviewRequest(
                project_name=request.project_name,
                scope="all-light",
                provider=request.provider,
                focus=request.question,
                show_sources=request.show_sources,
            )
        )
        return AgentRunResult(
            agent_name=result.agent_name,
            project_name=result.project_name,
            status=result.status,
            answer=result.summary,
            sources=result.sources,
            warnings=result.warnings,
            metadata=result.metadata,
        )

    def review(self, request: CodeReviewRequest) -> CodeReviewResult:
        if request.scope not in self._SCOPE_PATTERNS:
            raise AIContextError(f"Unknown review scope: {request.scope}")

        snapshot = self._memory_agent.snapshot(request.project_name)
        provider_name = (request.provider or self._settings.ai.default_provider).strip().lower()
        sources, warnings = self._load_review_sources(request)
        findings = self._deterministic_findings(request, sources)
        recommendations = self._recommendations(request)
        test_suggestions = self._test_suggestions(request)
        status = "ok"

        summary = self._format_review_summary(
            request=request,
            findings=findings,
            recommendations=recommendations,
            test_suggestions=test_suggestions,
            source_count=len(sources),
        )
        if provider_name == "mock":
            summary = "Read-only review mode.\n\n" + summary
        elif provider_name == "ollama":
            try:
                generated = self._ollama_review_summary(request, snapshot, sources, findings)
                if generated:
                    summary = generated
            except AIProviderError as exc:
                warnings.append(str(exc))
                status = "warning"
                summary = "Read-only review mode.\n\n" + summary
        else:
            raise AIProviderError(f"Unknown AI provider: {provider_name}")

        metadata = {
            "provider": provider_name,
            "source_count": len(sources),
            "scope": request.scope,
            "max_files": request.max_files,
            "max_chars_per_file": request.max_chars_per_file,
            "prompt_logged": False,
        }
        write_audit(
            event="agent_code_review_run",
            payload={
                "agent_name": self.agent_name,
                "provider": provider_name,
                "project": request.project_name,
                "scope": request.scope,
                "source_count": len(sources),
            },
            logs_root=get_logs_dir(),
            stream="tool-calls",
        )
        return CodeReviewResult(
            agent_name=self.agent_name,
            project_name=request.project_name,
            scope=request.scope,
            status=status,
            summary=summary,
            findings=findings,
            recommendations=recommendations,
            test_suggestions=test_suggestions,
            sources=sources,
            warnings=snapshot.warnings + warnings,
            metadata=metadata,
        )

    def _load_review_sources(self, request: CodeReviewRequest) -> tuple[list[AgentContextSource], list[str]]:
        selected = self._select_files(request.scope, request.files, request.max_files)
        warnings: list[str] = []
        sources: list[AgentContextSource] = []
        total_chars = 0
        for path in selected:
            if total_chars >= self._MAX_TOTAL_CONTEXT_CHARS:
                warnings.append(
                    f"Total review context capped at {self._MAX_TOTAL_CONTEXT_CHARS} chars; remaining files skipped."
                )
                break
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                warnings.append(f"Could not read {path}: {exc}")
                continue
            allowed = min(request.max_chars_per_file, self._MAX_TOTAL_CONTEXT_CHARS - total_chars)
            trimmed = content[:allowed]
            sources.append(
                AgentContextSource(
                    source_type="review-file",
                    label=path.name,
                    path=str(path.resolve()),
                    char_count=len(trimmed),
                    metadata={
                        "scope": request.scope,
                        "truncated": len(content) > len(trimmed),
                        "original_char_count": len(content),
                    },
                )
            )
            total_chars += len(trimmed)
        return sources, warnings

    def _select_files(self, scope: str, explicit_files: list[str], max_files: int) -> list[Path]:
        root = get_atlas_root()
        selected: list[Path] = []
        seen: set[Path] = set()
        for pattern in self._SCOPE_PATTERNS[scope]:
            for path in root.glob(pattern):
                if len(selected) >= max_files:
                    break
                if path.is_file() and self._is_allowed_path(path):
                    resolved = path.resolve()
                    if resolved not in seen:
                        seen.add(resolved)
                        selected.append(resolved)
            if len(selected) >= max_files:
                break
        for raw in explicit_files:
            if len(selected) >= max_files:
                break
            path = Path(raw)
            resolved = (root / path).resolve() if not path.is_absolute() else path.resolve()
            if resolved.is_file() and self._is_allowed_path(resolved) and resolved not in seen:
                seen.add(resolved)
                selected.append(resolved)
        return sorted(selected, key=lambda item: str(item).lower())[:max_files]

    def _is_allowed_path(self, path: Path) -> bool:
        resolved = path.resolve()
        root = get_atlas_root().resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            return False
        lower = str(resolved).lower()
        if any(token in lower for token in self._BLOCKED_PATH_TOKENS):
            return False
        if any(part == "__pycache__" for part in resolved.parts):
            return False
        if resolved.name.lower() in self._BLOCKED_NAMES:
            return False
        if resolved.suffix.lower() in self._BLOCKED_SUFFIXES:
            return False
        return True

    def _deterministic_findings(
        self,
        request: CodeReviewRequest,
        sources: list[AgentContextSource],
    ) -> list[CodeReviewFinding]:
        first_path = sources[0].path if sources else "(no file selected)"
        findings = [
            CodeReviewFinding(
                severity="low",
                category="ai-safety",
                title="Read-only boundary should stay explicit",
                description="Review yuzeyi bounded ve read-only kalmali; capability flag'leri ve scope guard'lari testlerle korunmali.",
                affected_file=first_path,
                evidence=f"Scope={request.scope}, reviewed_files={len(sources)}",
                recommendation="Yeni review akislari eklenirse write/command/tool flag'leri icin regresyon testleri zorunlu tutulmali.",
                test_suggestion="Agent capability flag'leri ve CLI smoke testleri her sprintte calismali.",
            )
        ]
        if request.scope in {"config", "mcp"}:
            findings.append(
                CodeReviewFinding(
                    severity="medium",
                    category="configuration",
                    title="Config drift riski var",
                    description="JSON config, CLI opsiyonlari ve runtime beklentileri senkron kalmazsa review yanlis yorum uretebilir.",
                    affected_file=first_path,
                    evidence="Config scope only reads a bounded subset of JSON and config modules.",
                    recommendation="Config degisikliklerinde CLI regression testleri ve schema smoke testleri birlikte kosulmali.",
                    test_suggestion="config validate ve scope bazli ai review CLI testleri korunmali.",
                )
            )
        if request.scope in {"ai-layer", "architecture"}:
            findings.append(
                CodeReviewFinding(
                    severity="medium",
                    category="architecture",
                    title="Agent sorumluluklari dar tutulmali",
                    description="Memory, QA, Planner ve Review katmanlari buyudukce sorumluluk sinirlari bulanabilir.",
                    affected_file=first_path,
                    evidence="Review scope includes agent and AI-layer modules together.",
                    recommendation="Yeni agentlar sadece kendi bounded contract'i uzerinden baglanmali.",
                    test_suggestion="Yeni agent eklendiginde mevcut ai ask-agent / ai plan / ai review komutlari icin smoke test eklenmeli.",
                )
            )
        if request.include_tests:
            findings.append(
                CodeReviewFinding(
                    severity="info",
                    category="testing",
                    title="Review sonucu patch degil, test girdisi uretir",
                    description="CodeReviewerAgent sadece bulgu ve test onerisi vermeli; otomatik fix yuzeyi olusmamali.",
                    affected_file=first_path,
                    evidence="Review command returns structured findings without patch generation.",
                    recommendation="Findings ile patch uygulama yuzeyleri ayrik komutlarda tutulmali.",
                    test_suggestion="CLI JSON output ve show-sources davranisi icin assertions korunmali.",
                )
            )
        return findings

    def _recommendations(self, request: CodeReviewRequest) -> list[ReviewRecommendation]:
        return [
            ReviewRecommendation(
                title="Scoped review discipline",
                text=f"`{request.scope}` scope'u disina cikmadan bulgulari spesifik dosya ve test onerileriyle sinirli tut.",
            ),
            ReviewRecommendation(
                title="Explicit approval boundary",
                text="Bu sprint review-only. Herhangi bir duzeltme veya patch uygulamasi ayri kullanici onayi gerektirir.",
            ),
        ]

    def _test_suggestions(self, request: CodeReviewRequest) -> list[ReviewTestSuggestion]:
        return [
            ReviewTestSuggestion(text="python -m pytest -q"),
            ReviewTestSuggestion(text="python -m app.cli doctor --full"),
            ReviewTestSuggestion(text=f"python -m app.cli ai review --project {request.project_name} --provider mock --scope {request.scope}"),
        ]

    def _ollama_review_summary(
        self,
        request: CodeReviewRequest,
        snapshot,
        sources: list[AgentContextSource],
        findings: list[CodeReviewFinding],
    ) -> str:
        provider = OllamaAIProvider(self._settings.ai.ollama)
        health = provider.health_check()
        if not health.ok:
            raise AIProviderError(health.message)
        bundle = AIContextBundle(
            project=request.project_name,
            sources=[
                AIContextSource(
                    kind="review",
                    label=source.label,
                    path=source.path,
                    content=self._read_trimmed(Path(source.path), source.char_count),
                    metadata={"char_count": source.char_count, **source.metadata},
                )
                for source in sources
            ],
            metadata={"total_chars": sum(source.char_count for source in sources), "max_total_chars": self._MAX_TOTAL_CONTEXT_CHARS},
        )
        prompt = (
            "You are CodeReviewerAgent in read-only advisory mode.\n"
            "Do not claim you changed files.\n"
            "Do not claim you ran commands.\n"
            "Produce a bounded review only.\n"
            "List risks, testing gaps, and actionable follow-ups.\n"
            "Ask for explicit approval before any implementation.\n"
            "Yaniti Turkce ver.\n\n"
            f"Proje: {request.project_name}\n"
            f"Scope: {request.scope}\n"
            f"Odak: {request.focus or 'genel review'}\n"
            f"Current status:\n{snapshot.current_status[:1200]}\n\n"
            "On bulgular:\n"
            + "\n".join(f"- {item.severity}/{item.category}: {item.title}" for item in findings[:6])
            + "\n\nKisa ama actionable bir review ozeti ver."
        )
        return provider.generate(prompt=prompt, context=bundle).text

    def _read_trimmed(self, path: Path, char_count: int) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="replace")[:char_count]
        except OSError:
            return ""

    def _format_review_summary(
        self,
        *,
        request: CodeReviewRequest,
        findings: list[CodeReviewFinding],
        recommendations: list[ReviewRecommendation],
        test_suggestions: list[ReviewTestSuggestion],
        source_count: int,
    ) -> str:
        lines = [
            f"Project: {request.project_name}",
            f"Scope: {request.scope}",
            f"Reviewed sources: {source_count}",
            "",
            "Findings:",
        ]
        if findings:
            lines.extend(f"- [{item.severity}] {item.category}: {item.title} -> {item.affected_file}" for item in findings)
        else:
            lines.append("- No critical findings in the bounded review scope.")
        lines.extend(["", "Recommendations:"])
        lines.extend(f"- {item.title}: {item.text}" for item in recommendations)
        lines.extend(["", "Test suggestions:"])
        lines.extend(f"- {item.text}" for item in test_suggestions)
        lines.extend(["", "Explicit approval is required before any implementation."])
        return "\n".join(lines)
