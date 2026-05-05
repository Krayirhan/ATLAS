"""MainAgent: deterministic coordinator over read-only sub-agents."""

from __future__ import annotations

import re
from dataclasses import asdict

from app.agents.base import BaseAgent
from app.agents.code_reviewer_agent import CodeReviewerAgent
from app.agents.documentation_agent import DocumentationAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.models import (
    AgentContextSource,
    AgentOrchestrationStep,
    AgentRouteDecision,
    AgentRunRequest,
    AgentRunResult,
    AgentSafetySummary,
    CodeReviewRequest,
    DocumentationAuditRequest,
    MainAgentRequest,
    MainAgentResult,
    PlannerRequest,
    ProjectQARequest,
    SecurityAuditRequest,
)
from app.agents.planner_agent import PlannerAgent
from app.agents.project_qa_agent import ProjectQAAgent
from app.agents.security_auditor_agent import SecurityAuditorAgent
from app.agents.tool_approval_agent import ToolApprovalAgent
from app.approval.models import ProposedCommand
from app.ai.providers.base import AIProviderError
from app.logging.audit import write_audit
from app.paths import get_logs_dir


class MainAgent(BaseAgent):
    agent_name = "main-agent"

    def __init__(
        self,
        *,
        memory_agent: MemoryAgent | None = None,
        qa_agent: ProjectQAAgent | None = None,
        planner_agent: PlannerAgent | None = None,
        review_agent: CodeReviewerAgent | None = None,
        security_agent: SecurityAuditorAgent | None = None,
        approval_agent: ToolApprovalAgent | None = None,
        documentation_agent: DocumentationAgent | None = None,
    ) -> None:
        self._memory_agent = memory_agent or MemoryAgent()
        self._qa_agent = qa_agent or ProjectQAAgent(memory_agent=self._memory_agent)
        self._planner_agent = planner_agent or PlannerAgent(memory_agent=self._memory_agent)
        self._review_agent = review_agent or CodeReviewerAgent(memory_agent=self._memory_agent)
        self._security_agent = security_agent or SecurityAuditorAgent()
        self._approval_agent = approval_agent or ToolApprovalAgent()
        self._documentation_agent = documentation_agent or DocumentationAgent()

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        result = self.handle(
            MainAgentRequest(
                project_name=request.project_name,
                user_message=request.question,
                provider=request.provider,
                show_sources=request.show_sources,
                show_routing=request.show_context,
            )
        )
        return AgentRunResult(
            agent_name=result.agent_name,
            project_name=result.project_name,
            status="ok" if not result.warnings else "warning",
            answer=result.answer,
            sources=result.sources,
            warnings=result.warnings,
            metadata=result.metadata,
        )

    def handle(self, request: MainAgentRequest) -> MainAgentResult:
        route = self._route(request)
        warnings: list[str] = []
        sources: list[AgentContextSource] = []
        sub_results: list[dict[str, object]] = []
        steps: list[AgentOrchestrationStep] = []
        answer = ""
        summary = ""
        response_mode = "answer"

        try:
            if route.task_type in {"project_question", "project_status", "report_question", "unknown"}:
                snapshot = self._memory_agent.snapshot(request.project_name)
                qa = self._qa_agent.answer(
                    ProjectQARequest(
                        project_name=request.project_name,
                        question=request.user_message,
                        provider=request.provider,
                        show_sources=request.show_sources,
                    )
                )
                sources = self._merge_sources(snapshot.context_sources, qa.sources)
                warnings.extend(snapshot.warnings)
                warnings.extend(qa.warnings)
                answer = qa.answer
                summary = "Project question handled via MemoryAgent + ProjectQAAgent."
                response_mode = "answer"
                sub_results.extend(
                    [
                        {"agent_name": "memory-agent", "status": "ok", "summary": "Snapshot loaded."},
                        {"agent_name": qa.agent_name, "status": qa.status, "summary": qa.answer[:240]},
                    ]
                )
                steps.extend(
                    [
                        AgentOrchestrationStep("load-memory", "memory-agent", "Project snapshot", "ok", "Snapshot loaded."),
                        AgentOrchestrationStep("answer-question", qa.agent_name, "Project QA", qa.status, qa.answer[:240]),
                    ]
                )
            elif route.task_type == "documentation_question":
                doc_scope = self._documentation_scope(request.user_message.lower())
                doc_result = self._documentation_agent.audit(
                    DocumentationAuditRequest(
                        project_name=request.project_name,
                        scope=doc_scope,
                        provider=request.provider,
                        show_sources=request.show_sources,
                    )
                )
                sources = doc_result.sources
                warnings.extend(doc_result.warnings)
                answer = doc_result.summary
                summary = f"Documentation audit handled via DocumentationAgent ({doc_scope})."
                response_mode = "review"
                sub_results.append({"agent_name": doc_result.agent_name, "status": doc_result.status, "summary": doc_result.summary[:240]})
                steps.append(AgentOrchestrationStep("documentation-audit", doc_result.agent_name, "Bounded documentation audit", doc_result.status, doc_result.summary[:240]))
            elif route.task_type == "sprint_plan":
                result = self._planner_agent.plan(
                    PlannerRequest(
                        project_name=request.project_name,
                        goal=request.user_message,
                        provider=request.provider,
                        show_sources=request.show_sources,
                    )
                )
                sources = result.sources
                warnings.extend(result.warnings)
                answer = result.plan_summary
                summary = "Planning request handled via PlannerAgent."
                response_mode = "plan"
                sub_results.append({"agent_name": result.agent_name, "status": result.status, "summary": result.plan_summary[:240]})
                steps.append(AgentOrchestrationStep("build-plan", result.agent_name, "Sprint planning", result.status, result.plan_summary[:240]))
            elif route.task_type == "security_review" and "security-auditor-agent" in route.selected_agents:
                audit_scope = self._security_scope(request.user_message.lower())
                result = self._security_agent.audit(
                    SecurityAuditRequest(
                        project_name=request.project_name,
                        scope=audit_scope,
                        provider=request.provider,
                        show_sources=request.show_sources,
                    )
                )
                sources = result.sources
                warnings.extend(result.warnings)
                answer = result.summary
                summary = f"Security audit handled via SecurityAuditorAgent ({audit_scope})."
                response_mode = "review"
                sub_results.append({"agent_name": result.agent_name, "status": result.status, "summary": result.summary[:240]})
                steps.append(AgentOrchestrationStep("security-audit", result.agent_name, "Bounded security audit", result.status, result.summary[:240]))
            elif route.task_type in {"code_review", "security_review"}:
                review_scope = self._review_scope(request.user_message.lower(), route.task_type)
                result = self._review_agent.review(
                    CodeReviewRequest(
                        project_name=request.project_name,
                        scope=review_scope,
                        provider=request.provider,
                        focus=request.user_message,
                        show_sources=request.show_sources,
                    )
                )
                sources = result.sources
                warnings.extend(result.warnings)
                answer = result.summary
                summary = f"Review request handled via CodeReviewerAgent ({review_scope})."
                response_mode = "review"
                sub_results.append({"agent_name": result.agent_name, "status": result.status, "summary": result.summary[:240]})
                steps.append(AgentOrchestrationStep("review-scope", result.agent_name, "Bounded review", result.status, result.summary[:240]))
            elif route.task_type == "approval_check":
                command = self._extract_command(request.user_message)
                decision = self._approval_agent.evaluate_command(
                    ProposedCommand(
                        project_name=request.project_name,
                        command=command,
                        source_agent=self.agent_name,
                        reason="MainAgent approval preview",
                        user_goal=request.user_message,
                    )
                )
                answer = self._approval_agent._format_decision(decision)
                summary = "Approval check handled via ToolApprovalAgent."
                response_mode = "approval_preview"
                warnings.extend([] if not decision.blocked else ["Blocked action preview only."])
                sub_results.append({"agent_name": "tool-approval-agent", "status": decision.status, "summary": decision.reason})
                steps.append(AgentOrchestrationStep("approval-check", "tool-approval-agent", "Command safety preview", decision.status, decision.reason))
            else:
                answer = (
                    "Istek net siniflandirilamadi. Read-only sinir korunuyor. "
                    "Daha dar bir soru, plan, review veya approval preview istegi verin."
                )
                summary = "Unknown route fallback."
                response_mode = "refusal_or_warning"
                warnings.append("Unknown route; no action executed.")
                steps.append(AgentOrchestrationStep("fallback", self.agent_name, "Graceful fallback", "warning", answer))
        except AIProviderError as exc:
            answer = (
                "Alt agent yaniti tamamlanamadi. Runtime veya provider warning var. "
                "Read-only sinir korunuyor; hicbir komut veya dosya islemi yapilmadi.\n\n"
                f"Detay: {exc}"
            )
            summary = "Provider warning during orchestration."
            warnings.append(str(exc))
            response_mode = "refusal_or_warning"
            steps.append(AgentOrchestrationStep("provider-warning", self.agent_name, "Graceful provider fallback", "warning", str(exc)))

        safety = AgentSafetySummary(
            read_only=self.read_only,
            can_write_files=self.can_write_files,
            can_run_commands=self.can_run_commands,
            can_call_tools=self.can_call_tools,
            approval_token_production=False,
        )
        metadata = {
            "route": asdict(route),
            "steps": [asdict(step) for step in steps],
            "source_count": len(sources),
            "show_routing": request.show_routing,
            "provider": request.provider or "default",
        }
        write_audit(
            event="agent_main_run",
            payload={
                "agent_name": self.agent_name,
                "project": request.project_name,
                "task_type": route.task_type,
                "selected_agents": route.selected_agents,
                "response_mode": response_mode,
                "source_count": len(sources),
            },
            logs_root=get_logs_dir(),
            stream="tool-calls",
        )
        return MainAgentResult(
            agent_name=self.agent_name,
            project_name=request.project_name,
            task_type=route.task_type,
            response_mode=response_mode,
            route=route,
            answer=answer,
            summary=summary,
            sources=sources,
            warnings=warnings,
            safety=safety,
            sub_results=sub_results,
            metadata=metadata,
        )

    def _route(self, request: MainAgentRequest) -> AgentRouteDecision:
        message = self._normalize_tr(request.user_message.lower().strip())
        if self._looks_like_command_safety(message):
            return AgentRouteDecision(
                task_type="approval_check",
                selected_agents=["tool-approval-agent"],
                reason="Command/tool safety keywords detected.",
                confidence=0.96,
                requires_approval_check=True,
                blocked_by_policy=False,
            )
        if self._looks_like_security_audit(message, request.preferred_mode):
            return AgentRouteDecision(
                task_type="security_review",
                selected_agents=["security-auditor-agent"],
                reason="Security audit keywords detected.",
                confidence=0.93,
                requires_approval_check=False,
                blocked_by_policy=False,
            )
        if self._looks_like_plan(message, request.preferred_mode):
            return AgentRouteDecision(
                task_type="sprint_plan",
                selected_agents=["memory-agent", "planner-agent"],
                reason="Planning keywords or requested plan mode detected.",
                confidence=0.91,
                requires_approval_check=False,
                blocked_by_policy=False,
            )
        if self._looks_like_review(message, request.preferred_mode):
            task_type = "security_review" if any(word in message for word in ("guvenli", "security", "safety", "mcp")) else "code_review"
            return AgentRouteDecision(
                task_type=task_type,
                selected_agents=["memory-agent", "code-reviewer-agent"],
                reason="Review/security keywords detected.",
                confidence=0.9,
                requires_approval_check=False,
                blocked_by_policy=False,
            )
        if any(word in message for word in ("durum", "ne durumda", "tamam mi", "calisiyor mu", "soru", "neden")):
            task_type = "project_status" if any(word in message for word in ("durum", "ne durumda", "calisiyor mu")) else "project_question"
            return AgentRouteDecision(
                task_type=task_type,
                selected_agents=["memory-agent", "project-qa-agent"],
                reason="Project question/status keywords detected.",
                confidence=0.88,
                requires_approval_check=False,
                blocked_by_policy=False,
            )
        if any(word in message for word in ("dokuman", "readme", "notebooklm", "roadmap", "sprint doküman", "sprint dokuman")):
            task = "documentation_question"
            return AgentRouteDecision(
                task_type=task,
                selected_agents=["documentation-agent"],
                reason="Documentation audit keywords detected.",
                confidence=0.88,
                requires_approval_check=False,
                blocked_by_policy=False,
            )
        if any(word in message for word in ("rapor", "report")):
            task = "report_question"
            return AgentRouteDecision(
                task_type=task,
                selected_agents=["memory-agent", "project-qa-agent"],
                reason="Report keywords detected.",
                confidence=0.75,
                requires_approval_check=False,
                blocked_by_policy=False,
            )
        return AgentRouteDecision(
            task_type="unknown",
            selected_agents=["memory-agent", "project-qa-agent"],
            reason="Fallback route for ambiguous request.",
            confidence=0.45,
            requires_approval_check=False,
            blocked_by_policy=False,
        )

    def _looks_like_plan(self, message: str, preferred_mode: str) -> bool:
        return preferred_mode == "plan" or any(word in message for word in ("plan", "sprint", "sonraki", "hazir", "nasil yapil"))

    def _looks_like_security_audit(self, message: str, preferred_mode: str) -> bool:
        if preferred_mode == "security":
            return True
        tokens = (
            # English
            "security audit",
            "audit security",
            "full disk",
            "secret leakage",
            "prompt logging",
            # Turkish — ASCII-normalized (ü→u, ğ→g, ş→s, ç→c, ı→i, ö→o)
            "guvenlik",
            "guvenli mi",
            "guvenlik denet",
            "atlas guvenli mi",
            "mcp guvenli mi",
            "mcp config guvenli mi",
            "agentlarda yazma yetkisi",
            "yazma yetkisi acilmis mi",
            "approval policy guvenli mi",
            "toolapproval guvenli mi",
            ".env okunuyor",
            "d:\\atlas",
        )
        return any(token in message for token in tokens)

    def _looks_like_review(self, message: str, preferred_mode: str) -> bool:
        return preferred_mode == "review" or any(word in message for word in ("incele", "review", "guvenli mi", "safety", "security", "mcp config", "ai layer"))

    def _looks_like_command_safety(self, message: str) -> bool:
        command_tokens = ("git ", "pytest", "doctor --full", "pip install", "npm install", "docker run", "reset --hard", "remove-item")
        if any(token in message for token in command_tokens):
            return True
        if "approval" in message:
            return True
        return ("guvenli mi" in message or "riskli mi" in message) and ("komut" in message or "command" in message or "tool" in message)

    def _review_scope(self, message: str, task_type: str) -> str:
        if "mcp" in message:
            return "mcp"
        if "config" in message:
            return "config"
        if task_type == "security_review" or any(word in message for word in ("safety", "security", "guvenli")):
            return "safety"
        if "test" in message:
            return "tests"
        if "docs" in message or "readme" in message:
            return "docs"
        return "ai-layer"

    def _documentation_scope(self, message: str) -> str:
        if "notebooklm" in message:
            return "notebooklm"
        if "roadmap" in message or "sprint" in message:
            return "roadmap"
        if "agent" in message:
            return "agents"
        if "readme" in message:
            return "readme"
        if "release" in message or "checklist" in message:
            return "release"
        if "kb" in message or "knowledge" in message:
            return "knowledge-base"
        return "all-light"

    def _security_scope(self, message: str) -> str:
        if "mcp" in message:
            return "mcp"
        if "approval" in message or "git reset" in message or "git push" in message:
            return "approval"
        if any(token in message for token in ("secret", ".env", "key", "keystore")):
            return "secrets"
        if any(token in message for token in ("context", "prompt", "source index")):
            return "context"
        if "doc" in message or "readme" in message:
            return "docs"
        if any(token in message for token in ("agent", "write permission", "yazma yetkisi")):
            return "agents"
        return "all-light"

    def _extract_command(self, message: str) -> str:
        lowered = message.lower()
        if "git reset --hard" in lowered:
            return "git reset --hard"
        if "git push" in lowered:
            return "git push"
        if "python -m pytest -q" in lowered or "pytest" in lowered:
            return "python -m pytest -q"
        if "python -m app.cli doctor --full" in lowered or "doctor --full" in lowered:
            return "python -m app.cli doctor --full"
        quoted = re.findall(r'"([^"]+)"', message)
        if quoted:
            return quoted[0]
        return message

    def _merge_sources(self, *groups: list[AgentContextSource]) -> list[AgentContextSource]:
        merged: list[AgentContextSource] = []
        seen: set[tuple[str, str]] = set()
        for group in groups:
            for source in group:
                key = (source.label, source.path)
                if key not in seen:
                    seen.add(key)
                    merged.append(source)
        return merged

    @staticmethod
    def _normalize_tr(text: str) -> str:
        """Normalize Turkish diacritics to ASCII for robust keyword matching.

        ü→u, ö→o, ğ→g, ş→s, ç→c, ı→i  (lowercase only; call after .lower()).
        Keeps all other characters unchanged.
        """
        return text.translate(
            str.maketrans(
                {
                    "ü": "u",
                    "ö": "o",
                    "ğ": "g",
                    "ş": "s",
                    "ç": "c",
                    "ı": "i",
                }
            )
        )
