"""SecurityAuditorAgent: bounded read-only security audit over ATLAS surfaces."""

from __future__ import annotations

import json
from pathlib import Path

from app.agents.base import BaseAgent
from app.agents.models import (
    AgentCapabilityCheck,
    AgentContextSource,
    AgentRunRequest,
    AgentRunResult,
    ApprovalPolicyCheck,
    MCPExposureCheck,
    SecretExposureCheck,
    SecurityAuditFinding,
    SecurityAuditRequest,
    SecurityAuditResult,
    SecurityControlCheck,
)
from app.ai.context_loader import AIContextError
from app.ai.models import AIContextBundle, AIContextSource
from app.ai.providers.base import AIProviderError
from app.ai.providers.ollama_provider import OllamaAIProvider
from app.approval.evaluator import ApprovalEvaluator
from app.approval.models import ProposedCommand
from app.config.loader import load_assistant_settings, load_safety_policy
from app.logging.audit import write_audit
from app.paths import get_atlas_root, get_configs_dir, get_logs_dir


class SecurityAuditorAgent(BaseAgent):
    agent_name = "security-auditor-agent"
    _MAX_TOTAL_CONTEXT_CHARS = 14000
    _SCOPE_PATTERNS = {
        "agents": [
            "assistant-core/app/agents/base.py",
            "assistant-core/app/agents/models.py",
            "assistant-core/app/agents/memory_agent.py",
            "assistant-core/app/agents/project_qa_agent.py",
            "assistant-core/app/agents/planner_agent.py",
            "assistant-core/app/agents/code_reviewer_agent.py",
            "assistant-core/app/agents/tool_approval_agent.py",
            "assistant-core/app/agents/main_agent.py",
            "assistant-core/app/agents/security_auditor_agent.py",
        ],
        "mcp": [
            "configs/mcp.master.json",
            "configs/generated/cursor.mcp.json",
            "configs/generated/vscode.mcp.json",
            "configs/generated/codex.config.toml",
            "mcp-servers/project-memory-mcp/server.py",
            "mcp-servers/safe-terminal-mcp/server.py",
        ],
        "secrets": [
            "configs/safety-policy.json",
            "assistant-core/app/safety/*.py",
            "assistant-core/app/approval/*.py",
            "assistant-core/app/ai/context_loader.py",
            "assistant-core/app/agents/memory_agent.py",
        ],
        "approval": [
            "assistant-core/app/approval/models.py",
            "assistant-core/app/approval/evaluator.py",
            "assistant-core/app/approval/policy.py",
            "assistant-core/app/agents/tool_approval_agent.py",
            "assistant-core/app/commands/ai.py",
            "configs/safety-policy.json",
        ],
        "context": [
            "assistant-core/app/ai/context_loader.py",
            "assistant-core/app/ai/prompt_composer.py",
            "assistant-core/app/ai/service.py",
            "assistant-core/app/agents/memory_agent.py",
            "workspace/knowledge-base/ATLAS/11-ai-context-contract.md",
            "workspace/knowledge-base/ATLAS/12-ai-prompt-policy.md",
            "workspace/knowledge-base/ATLAS/15-ai-security-boundaries.md",
            "workspace/knowledge-base/ATLAS/16-ai-source-index.md",
        ],
        "docs": [
            "README.md",
            "assistant-core/README.md",
            "workspace/knowledge-base/ATLAS/03-current-status.md",
            "workspace/knowledge-base/ATLAS/04-risk-list.md",
            "workspace/knowledge-base/ATLAS/06-next-sprints.md",
            "workspace/knowledge-base/ATLAS/07-v1-rc-go-report.md",
            "workspace/knowledge-base/ATLAS/15-ai-security-boundaries.md",
        ],
        "all-light": [
            "configs/safety-policy.json",
            "configs/mcp.master.json",
            "configs/generated/cursor.mcp.json",
            "configs/generated/vscode.mcp.json",
            "configs/generated/codex.config.toml",
            "workspace/knowledge-base/ATLAS/04-risk-list.md",
            "workspace/knowledge-base/ATLAS/06-next-sprints.md",
            "workspace/knowledge-base/ATLAS/16-ai-source-index.md",
            "assistant-core/app/agents/base.py",
            "assistant-core/app/approval/evaluator.py",
        ],
    }
    _BLOCKED_NAMES = {".env", ".env.local", "id_rsa", "id_ed25519", "known_hosts"}
    _BLOCKED_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".kdbx", ".jks", ".keystore"}
    _BLOCKED_PATH_TOKENS = {"d:\\atlas", "c:\\users", "appdata", "browser profile"}

    def __init__(self) -> None:
        self._settings = load_assistant_settings()
        self._approval_evaluator = ApprovalEvaluator()

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        result = self.audit(
            SecurityAuditRequest(
                project_name=request.project_name,
                scope="all-light",
                provider=request.provider,
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

    def audit(self, request: SecurityAuditRequest) -> SecurityAuditResult:
        if request.scope not in self._SCOPE_PATTERNS:
            raise AIContextError(f"Unknown security audit scope: {request.scope}")

        sources, warnings = self._load_sources(request)
        findings: list[SecurityAuditFinding] = []
        controls: list[SecurityControlCheck] = []
        capability_checks: list[AgentCapabilityCheck] = []
        mcp_checks: list[MCPExposureCheck] = []
        secret_checks: list[SecretExposureCheck] = []
        approval_checks: list[ApprovalPolicyCheck] = []

        if request.include_agents and request.scope in {"agents", "all-light"}:
            cap_findings, cap_controls, cap_checks = self._check_agent_capabilities()
            findings.extend(cap_findings)
            controls.extend(cap_controls)
            capability_checks.extend(cap_checks)
        if request.include_mcp and request.scope in {"mcp", "all-light"}:
            mcp_findings, mcp_controls, checks = self._check_mcp_exposure()
            findings.extend(mcp_findings)
            controls.extend(mcp_controls)
            mcp_checks.extend(checks)
        if request.include_safety_policy and request.scope in {"secrets", "all-light"}:
            sec_findings, sec_controls, checks = self._check_secret_exposure()
            findings.extend(sec_findings)
            controls.extend(sec_controls)
            secret_checks.extend(checks)
        if request.include_approval_policy and request.scope in {"approval", "all-light"}:
            ap_findings, ap_controls, checks = self._check_approval_policy()
            findings.extend(ap_findings)
            controls.extend(ap_controls)
            approval_checks.extend(checks)
        if request.include_context_sources and request.scope in {"context", "all-light"}:
            ctx_findings, ctx_controls = self._check_context_safety()
            findings.extend(ctx_findings)
            controls.extend(ctx_controls)
        if request.include_docs and request.scope in {"docs", "all-light"}:
            doc_findings, doc_controls = self._check_docs_alignment()
            findings.extend(doc_findings)
            controls.extend(doc_controls)

        decision = self._decision(findings)
        status = "ok" if decision == "GO" else "warning"
        recommendations = self._recommendations(findings)
        test_suggestions = self._test_suggestions(request.scope)
        summary = self._format_summary(request.scope, decision, findings, recommendations, test_suggestions)
        provider_name = (request.provider or self._settings.ai.default_provider).strip().lower()
        if provider_name == "ollama":
            try:
                summary = self._ollama_summary(request, findings, summary, sources)
            except AIProviderError as exc:
                warnings.append(str(exc))
                status = "warning"
        elif provider_name == "mock":
            summary = "Read-only security audit mode.\n\n" + summary

        metadata = {
            "provider": provider_name,
            "decision": decision,
            "scope": request.scope,
            "source_count": len(sources),
            "prompt_logged": False,
        }
        write_audit(
            event="agent_security_audit_run",
            payload={
                "agent_name": self.agent_name,
                "project": request.project_name,
                "scope": request.scope,
                "decision": decision,
                "source_count": len(sources),
            },
            logs_root=get_logs_dir(),
            stream="tool-calls",
        )
        return SecurityAuditResult(
            agent_name=self.agent_name,
            project_name=request.project_name,
            scope=request.scope,
            status=status,
            decision=decision,
            summary=summary,
            findings=findings,
            controls=controls,
            agent_capabilities=capability_checks,
            mcp_exposure=mcp_checks,
            secret_exposure=secret_checks,
            approval_policy=approval_checks,
            recommendations=recommendations,
            test_suggestions=test_suggestions,
            sources=sources,
            warnings=warnings,
            metadata=metadata,
        )

    def _load_sources(self, request: SecurityAuditRequest) -> tuple[list[AgentContextSource], list[str]]:
        selected = self._select_files(request.scope, request.max_files)
        sources: list[AgentContextSource] = []
        warnings: list[str] = []
        total_chars = 0
        for path in selected:
            if total_chars >= self._MAX_TOTAL_CONTEXT_CHARS:
                warnings.append(f"Total security audit context capped at {self._MAX_TOTAL_CONTEXT_CHARS} chars; remaining files skipped.")
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
                    source_type="security-audit-file",
                    label=path.name,
                    path=str(path.resolve()),
                    char_count=len(trimmed),
                    metadata={"scope": request.scope, "truncated": len(content) > len(trimmed), "original_char_count": len(content)},
                )
            )
            total_chars += len(trimmed)
        latest_audit = self._latest_v1_audit_report()
        if latest_audit and request.scope == "all-light":
            sources.append(
                AgentContextSource(
                    source_type="report",
                    label=latest_audit.name,
                    path=str(latest_audit.resolve()),
                    char_count=0,
                    metadata={"path_only": True},
                )
            )
        return sources, warnings

    def _select_files(self, scope: str, max_files: int) -> list[Path]:
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

    def _check_agent_capabilities(self):
        from app.agents.code_reviewer_agent import CodeReviewerAgent
        from app.agents.documentation_agent import DocumentationAgent
        from app.agents.main_agent import MainAgent
        from app.agents.memory_agent import MemoryAgent
        from app.agents.planner_agent import PlannerAgent
        from app.agents.project_qa_agent import ProjectQAAgent
        from app.agents.tool_approval_agent import ToolApprovalAgent

        checks: list[AgentCapabilityCheck] = []
        findings: list[SecurityAuditFinding] = []
        controls: list[SecurityControlCheck] = []
        agents = [
            MemoryAgent(),
            ProjectQAAgent(),
            PlannerAgent(),
            CodeReviewerAgent(),
            ToolApprovalAgent(),
            MainAgent(),
            DocumentationAgent(),
            self,
        ]
        for agent in agents:
            ok = agent.read_only and not agent.can_write_files and not agent.can_run_commands and not agent.can_call_tools
            status = "pass" if ok else "fail"
            detail = "Read-only flags are intact." if ok else "One or more capability flags are unsafe."
            checks.append(
                AgentCapabilityCheck(
                    agent_name=agent.agent_name,
                    read_only=agent.read_only,
                    can_write_files=agent.can_write_files,
                    can_run_commands=agent.can_run_commands,
                    can_call_tools=agent.can_call_tools,
                    status=status,
                    detail=detail,
                )
            )
            if not ok:
                findings.append(
                    SecurityAuditFinding(
                        severity="critical",
                        category="agent-capability",
                        title=f"Unsafe capability flags: {agent.agent_name}",
                        description="Agent capability flags indicate a write/run/tool surface.",
                        affected_file=f"agent:{agent.agent_name}",
                        evidence=detail,
                        recommendation="Agent flags must remain read_only=True and all mutable capabilities False.",
                        test_suggestion=f"Add/keep regression tests for {agent.agent_name} capability flags.",
                    )
                )
        controls.append(SecurityControlCheck("agent-capability-flags", "pass" if not findings else "fail", "All agent capability flags were checked."))
        return findings, controls, checks

    def _check_mcp_exposure(self):
        root = get_atlas_root()
        paths = [
            root / "configs" / "mcp.master.json",
            root / "configs" / "generated" / "cursor.mcp.json",
            root / "configs" / "generated" / "vscode.mcp.json",
            root / "configs" / "generated" / "codex.config.toml",
            root / "mcp-servers" / "project-memory-mcp" / "server.py",
            root / "mcp-servers" / "safe-terminal-mcp" / "server.py",
        ]
        checks: list[MCPExposureCheck] = []
        findings: list[SecurityAuditFinding] = []
        controls: list[SecurityControlCheck] = []
        for path in paths:
            if not path.is_file():
                checks.append(MCPExposureCheck(str(path), "warn", "File missing; review could not verify exposure."))
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            normalized = text.replace("\\\\", "\\")
            has_blocked_root = "C:\\Users" in normalized or "D:\\ATLAS" in normalized
            has_unbounded_filesystem = "@modelcontextprotocol/server-filesystem" in normalized and "E:\\ATLAS\\workspace" not in normalized
            if has_blocked_root or has_unbounded_filesystem:
                findings.append(
                    SecurityAuditFinding(
                        severity="critical",
                        category="mcp-exposure",
                        title="Unsafe MCP path exposure",
                        description="MCP config exposes blocked roots or unrestricted filesystem access.",
                        affected_file=str(path.resolve()),
                        evidence="Found blocked path token or missing bounded workspace root.",
                        recommendation="Keep filesystem MCP strictly bound to E:\\ATLAS\\workspace and remove blocked roots.",
                        test_suggestion="Validate generated MCP configs after any template change.",
                    )
                )
                checks.append(MCPExposureCheck(str(path.resolve()), "fail", "Blocked path exposure detected."))
            elif "ATLAS_SAFE_TERMINAL_APPROVAL_TOKEN" in text:
                checks.append(MCPExposureCheck(str(path.resolve()), "pass", "Token-gated run path detected; no unrestricted execution."))
            else:
                checks.append(MCPExposureCheck(str(path.resolve()), "pass", "No blocked MCP exposure detected."))
        controls.append(SecurityControlCheck("mcp-bounded-roots", "pass" if not findings else "fail", "MCP configs were checked for full-disk and blocked root exposure."))
        return findings, controls, checks

    def _check_secret_exposure(self):
        findings: list[SecurityAuditFinding] = []
        controls: list[SecurityControlCheck] = []
        checks: list[SecretExposureCheck] = []
        policy = load_safety_policy(get_configs_dir())
        required_patterns = {".env", "*.pem", "*.key", "*.keystore", "*.jks", "id_rsa", "id_ed25519"}
        missing = sorted(required_patterns - set(policy.blocked_file_patterns))
        if missing:
            findings.append(
                SecurityAuditFinding(
                    severity="high",
                    category="secret-exposure",
                    title="Safety policy is missing blocked secret patterns",
                    description="One or more blocked secret file patterns are missing from safety policy.",
                    affected_file=str((get_configs_dir() / "safety-policy.json").resolve()),
                    evidence=", ".join(missing),
                    recommendation="Restore the blocked file patterns list in safety-policy.json.",
                    test_suggestion="Add policy regression tests for blocked secret patterns.",
                )
            )
            checks.append(SecretExposureCheck("safety-policy-patterns", "fail", f"Missing: {', '.join(missing)}"))
        else:
            checks.append(SecretExposureCheck("safety-policy-patterns", "pass", "Secret patterns are explicitly blocked."))
        ctx = (get_atlas_root() / "assistant-core" / "app" / "ai" / "context_loader.py").read_text(encoding="utf-8", errors="replace")
        if ".env" in ctx or "C:\\Users" in ctx or "D:\\ATLAS" in ctx:
            findings.append(
                SecurityAuditFinding(
                    severity="critical",
                    category="secret-exposure",
                    title="Context loader references blocked secret or path tokens",
                    description="Context loader should not include secret files or blocked roots.",
                    affected_file=str((get_atlas_root() / "assistant-core" / "app" / "ai" / "context_loader.py").resolve()),
                    evidence="Found blocked token in context loader source.",
                    recommendation="Keep bounded context contract and secret exclusions intact.",
                    test_suggestion="Context loader tests should verify blocked source exclusion.",
                )
            )
            checks.append(SecretExposureCheck("context-loader-secret-paths", "fail", "Blocked token referenced in context loader."))
        else:
            checks.append(SecretExposureCheck("context-loader-secret-paths", "pass", "No blocked secret/path token found in context loader."))
        controls.append(SecurityControlCheck("secret-exposure-guard", "pass" if not findings else "fail", "Safety policy and context loader secret protections were checked."))
        return findings, controls, checks

    def _check_approval_policy(self):
        findings: list[SecurityAuditFinding] = []
        controls: list[SecurityControlCheck] = []
        checks: list[ApprovalPolicyCheck] = []
        expectations = {
            "git reset --hard": "blocked",
            "git push": "approval_required",
            "python -m app.cli doctor --full": "preview_allowed",
        }
        for command, expected in expectations.items():
            decision = self._approval_evaluator.evaluate_command(ProposedCommand(project_name="ATLAS", command=command))
            status = "pass" if decision.status == expected else "fail"
            checks.append(ApprovalPolicyCheck(command, status, f"expected={expected}, actual={decision.status}"))
            if decision.status != expected:
                findings.append(
                    SecurityAuditFinding(
                        severity="high",
                        category="approval-policy",
                        title=f"Unexpected approval decision for `{command}`",
                        description="Approval evaluator result diverges from expected governance policy.",
                        affected_file=str((get_atlas_root() / "assistant-core" / "app" / "approval" / "evaluator.py").resolve()),
                        evidence=f"expected={expected}, actual={decision.status}",
                        recommendation="Align approval evaluator with approved policy examples.",
                        test_suggestion="Keep approval evaluator regression tests for canonical commands.",
                    )
                )
        controls.append(SecurityControlCheck("approval-policy-expectations", "pass" if not findings else "fail", "Canonical approval decisions were checked."))
        return findings, controls, checks

    def _check_context_safety(self):
        findings: list[SecurityAuditFinding] = []
        controls: list[SecurityControlCheck] = []
        root = get_atlas_root()
        source_index = (root / "workspace" / "knowledge-base" / "ATLAS" / "16-ai-source-index.md").read_text(encoding="utf-8", errors="replace")
        contract = (root / "workspace" / "knowledge-base" / "ATLAS" / "11-ai-context-contract.md").read_text(encoding="utf-8", errors="replace")
        service = (root / "assistant-core" / "app" / "ai" / "service.py").read_text(encoding="utf-8", errors="replace")
        if "project-registry.json" not in source_index or "blocked sources" not in source_index.lower():
            findings.append(
                SecurityAuditFinding(
                    severity="medium",
                    category="context-source",
                    title="AI source index is incomplete",
                    description="Allowed/blocked context source contract is not explicit enough.",
                    affected_file=str((root / "workspace" / "knowledge-base" / "ATLAS" / "16-ai-source-index.md").resolve()),
                    evidence="Expected source index markers are missing.",
                    recommendation="Keep source index aligned with context contract and security boundaries.",
                    test_suggestion="Add doc checks for source index and context contract references.",
                )
            )
        if "Forbidden sources" not in contract and "Forbidden sources" not in contract.replace("forbidden", "Forbidden"):
            findings.append(
                SecurityAuditFinding(
                    severity="medium",
                    category="context-source",
                    title="Context contract missing forbidden source section",
                    description="Context contract should document blocked source classes clearly.",
                    affected_file=str((root / "workspace" / "knowledge-base" / "ATLAS" / "11-ai-context-contract.md").resolve()),
                    evidence="Forbidden source section not found.",
                    recommendation="Document blocked source classes in the context contract.",
                    test_suggestion="Add docs regression checks for forbidden source section.",
                )
            )
        service_lower = service.lower()
        if '"prompt":' in service_lower or "'prompt':" in service_lower:
            findings.append(
                SecurityAuditFinding(
                    severity="high",
                    category="prompt-logging",
                    title="Prompt may be written to audit metadata",
                    description="Prompt body should not appear in audit payloads.",
                    affected_file=str((root / "assistant-core" / "app" / "ai" / "service.py").resolve()),
                    evidence="Found suspicious prompt token in AI service audit path.",
                    recommendation="Keep audit logging metadata-only.",
                    test_suggestion="Add regression check for prompt body absence in audit payload builders.",
                )
            )
        controls.append(SecurityControlCheck("context-contract-alignment", "pass" if not findings else "warn", "Context source and prompt logging rules were checked."))
        return findings, controls

    def _check_docs_alignment(self):
        findings: list[SecurityAuditFinding] = []
        controls: list[SecurityControlCheck] = []
        root = get_atlas_root()
        current_status = (root / "workspace" / "knowledge-base" / "ATLAS" / "03-current-status.md").read_text(encoding="utf-8", errors="replace")
        risk_list = (root / "workspace" / "knowledge-base" / "ATLAS" / "04-risk-list.md").read_text(encoding="utf-8", errors="replace")
        if "MainAgent" not in current_status or "ToolApprovalAgent" not in current_status:
            findings.append(
                SecurityAuditFinding(
                    severity="low",
                    category="documentation",
                    title="Current status doc may be missing latest agent surface",
                    description="Security-sensitive agent surfaces should stay reflected in KB current status.",
                    affected_file=str((root / "workspace" / "knowledge-base" / "ATLAS" / "03-current-status.md").resolve()),
                    evidence="Expected agent names not found.",
                    recommendation="Keep current-status aligned with shipped agent surfaces.",
                    test_suggestion="Review KB status entries after each sprint.",
                )
            )
        if "Secret leakage" not in risk_list and "Secret leakage" not in risk_list.replace("secret leakage", "Secret leakage"):
            findings.append(
                SecurityAuditFinding(
                    severity="low",
                    category="documentation",
                    title="Risk list may not mention secret leakage risk",
                    description="Risk list should keep explicit AI secret leakage coverage.",
                    affected_file=str((root / "workspace" / "knowledge-base" / "ATLAS" / "04-risk-list.md").resolve()),
                    evidence="No secret leakage risk marker found.",
                    recommendation="Keep risk list aligned with AI security boundaries.",
                    test_suggestion="KB review should confirm AI-specific security risks stay present.",
                )
            )
        controls.append(SecurityControlCheck("security-doc-alignment", "pass" if not findings else "warn", "Security KB coverage was checked."))
        return findings, controls

    def _decision(self, findings: list[SecurityAuditFinding]) -> str:
        severities = {item.severity for item in findings}
        if "critical" in severities:
            return "NO-GO"
        if "high" in severities or "medium" in severities:
            return "CONDITIONAL"
        return "GO"

    def _recommendations(self, findings: list[SecurityAuditFinding]) -> list[str]:
        if not findings:
            return ["Read-only security controls korunuyor. Changes only after explicit user approval."]
        unique: list[str] = []
        for item in findings:
            if item.recommendation not in unique:
                unique.append(item.recommendation)
        return unique[:6]

    def _test_suggestions(self, scope: str) -> list[str]:
        return [
            "python -m pytest -q",
            "python -m app.cli doctor --full",
            f"python -m app.cli ai security-audit --project ATLAS --provider mock --scope {scope}",
        ]

    def _format_summary(self, scope: str, decision: str, findings: list[SecurityAuditFinding], recommendations: list[str], test_suggestions: list[str]) -> str:
        lines = [
            f"Decision: {decision}",
            f"Scope: {scope}",
            "",
            "Findings:",
        ]
        if findings:
            lines.extend(f"- [{item.severity}] {item.category}: {item.title} -> {item.affected_file}" for item in findings)
        else:
            lines.append("- No critical or high security blockers in the bounded audit scope.")
        lines.extend(["", "Recommendations:"])
        lines.extend(f"- {item}" for item in recommendations)
        lines.extend(["", "Test suggestions:"])
        lines.extend(f"- {item}" for item in test_suggestions)
        lines.extend(["", "No remediation is applied in this flow. Explicit approval is required before any implementation."])
        return "\n".join(lines)

    def _ollama_summary(self, request: SecurityAuditRequest, findings: list[SecurityAuditFinding], fallback: str, sources: list[AgentContextSource]) -> str:
        provider = OllamaAIProvider(self._settings.ai.ollama)
        health = provider.health_check()
        if not health.ok:
            raise AIProviderError(health.message)
        bundle = AIContextBundle(
            project=request.project_name,
            sources=[
                AIContextSource(
                    kind="security-audit",
                    label=source.label,
                    path=source.path,
                    content=f"path: {source.path}\nchar_count: {source.char_count}",
                    metadata=dict(source.metadata),
                )
                for source in sources[:8]
            ],
            metadata={"total_chars": sum(source.char_count for source in sources), "max_total_chars": self._MAX_TOTAL_CONTEXT_CHARS},
        )
        prompt = (
            "You are SecurityAuditorAgent in read-only advisory mode.\n"
            "Do not claim you changed files.\n"
            "Do not claim you ran commands.\n"
            "Summarize the bounded security audit in Turkish.\n"
            "Keep the deterministic decision intact.\n\n"
            + fallback
        )
        try:
            text = provider.generate(prompt=prompt, context=bundle).text
            return text or fallback
        except AIProviderError:
            raise

    def _latest_v1_audit_report(self) -> Path | None:
        reports_dir = get_atlas_root() / "workspace" / "outputs" / "reports" / "V1"
        if not reports_dir.is_dir():
            return None
        matches = sorted(reports_dir.glob("v1-rc-audit-*.md"), key=lambda path: path.stat().st_mtime, reverse=True)
        return matches[0] if matches else None
