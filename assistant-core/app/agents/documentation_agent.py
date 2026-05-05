"""DocumentationAgent: bounded read-only documentation audit over ATLAS surfaces."""

from __future__ import annotations

from pathlib import Path

from app.agents.base import BaseAgent
from app.agents.models import (
    AgentContextSource,
    AgentRunRequest,
    AgentRunResult,
    DocumentationAuditRequest,
    DocumentationAuditResult,
    DocumentationConsistencyCheck,
    DocumentationFinding,
    DocumentationRecommendation,
    DocumentationRoadmapCheck,
    DocumentationSourceCheck,
)
from app.ai.context_loader import AIContextError
from app.ai.models import AIContextBundle, AIContextSource
from app.ai.providers.base import AIProviderError
from app.ai.providers.ollama_provider import OllamaAIProvider
from app.config.loader import load_assistant_settings
from app.logging.audit import write_audit
from app.paths import get_atlas_root, get_logs_dir


class DocumentationAgent(BaseAgent):
    """Read-only documentation audit agent. Never writes files or runs commands."""

    agent_name = "documentation-agent"
    read_only = True
    can_write_files = False
    can_run_commands = False
    can_call_tools = False

    _MAX_TOTAL_CONTEXT_CHARS = 14000

    # Scope → relative paths from ATLAS root (globs supported)
    _SCOPE_PATTERNS: dict[str, list[str]] = {
        "readme": [
            "README.md",
            "assistant-core/README.md",
        ],
        "knowledge-base": [
            "workspace/knowledge-base/ATLAS/00-project-summary.md",
            "workspace/knowledge-base/ATLAS/03-current-status.md",
            "workspace/knowledge-base/ATLAS/04-risk-list.md",
            "workspace/knowledge-base/ATLAS/06-next-sprints.md",
            "workspace/knowledge-base/ATLAS/07-v1-rc-go-report.md",
        ],
        "notebooklm": [
            "workspace/knowledge-base/ATLAS/10-notebooklm-workflow.md",
            "workspace/notebooklm-exports/README.md",
            "workspace/notebooklm-exports/_templates/atlas-notebooklm-export-template.md",
            "workspace/notebooklm-exports/_templates/project-summary-export-template.md",
            "workspace/notebooklm-exports/_templates/sprint-report-export-template.md",
            "workspace/notebooklm-exports/_templates/risk-audit-export-template.md",
        ],
        "roadmap": [
            "workspace/knowledge-base/ATLAS/06-next-sprints.md",
            "workspace/knowledge-base/ATLAS/07-v1-rc-go-report.md",
            "README.md",
        ],
        "agents": [
            "workspace/knowledge-base/ATLAS/14-sprint-29-memory-agent-projectqa-plan.md",
            "workspace/knowledge-base/ATLAS/17-sprint-30-planner-agent-plan.md",
            "workspace/knowledge-base/ATLAS/18-sprint-31-code-reviewer-agent-plan.md",
            "workspace/knowledge-base/ATLAS/19-sprint-32-tool-approval-design.md",
            "workspace/knowledge-base/ATLAS/20-sprint-33-main-agent-alpha.md",
            "workspace/knowledge-base/ATLAS/21-sprint-34-security-auditor-agent.md",
            "README.md",
        ],
        "release": [
            "workspace/knowledge-base/ATLAS/05-release-checklist.md",
            "workspace/knowledge-base/ATLAS/07-v1-rc-go-report.md",
        ],
        "all-light": [
            "README.md",
            "assistant-core/README.md",
            "workspace/knowledge-base/ATLAS/03-current-status.md",
            "workspace/knowledge-base/ATLAS/06-next-sprints.md",
            "workspace/knowledge-base/ATLAS/07-v1-rc-go-report.md",
            "workspace/knowledge-base/ATLAS/10-notebooklm-workflow.md",
            "workspace/knowledge-base/ATLAS/14-sprint-29-memory-agent-projectqa-plan.md",
            "workspace/knowledge-base/ATLAS/17-sprint-30-planner-agent-plan.md",
            "workspace/knowledge-base/ATLAS/18-sprint-31-code-reviewer-agent-plan.md",
            "workspace/knowledge-base/ATLAS/19-sprint-32-tool-approval-design.md",
            "workspace/knowledge-base/ATLAS/20-sprint-33-main-agent-alpha.md",
            "workspace/knowledge-base/ATLAS/21-sprint-34-security-auditor-agent.md",
        ],
    }

    # Security: blocked file names / suffixes / path tokens
    _BLOCKED_NAMES = {".env", ".env.local", "id_rsa", "id_ed25519", "known_hosts"}
    _BLOCKED_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".kdbx", ".jks", ".keystore"}
    _BLOCKED_PATH_TOKENS = {"d:\\atlas", "c:\\users", "appdata", "browser profile"}

    def __init__(self) -> None:
        self._settings = load_assistant_settings()

    # ------------------------------------------------------------------
    # BaseAgent contract
    # ------------------------------------------------------------------

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        result = self.audit(
            DocumentationAuditRequest(
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

    # ------------------------------------------------------------------
    # Main audit method
    # ------------------------------------------------------------------

    def audit(self, request: DocumentationAuditRequest) -> DocumentationAuditResult:
        if request.scope not in self._SCOPE_PATTERNS:
            raise AIContextError(f"Unknown documentation audit scope: {request.scope!r}. "
                                 f"Valid: {', '.join(self._SCOPE_PATTERNS)}")

        sources, warnings = self._load_sources(request)
        content_map: dict[str, str] = {src.label: src.metadata.get("content", "") for src in sources}

        findings: list[DocumentationFinding] = []
        source_checks: list[DocumentationSourceCheck] = []
        roadmap_checks: list[DocumentationRoadmapCheck] = []
        consistency_checks: list[DocumentationConsistencyCheck] = []
        missing_docs: list[str] = []
        outdated_docs: list[str] = []

        # Run bounded checks
        sc, f = self._check_source_presence(request)
        source_checks.extend(sc)
        findings.extend(f)
        for item in source_checks:
            if item.status == "missing":
                missing_docs.append(item.label)

        rc, rf = self._check_roadmap(sources)
        roadmap_checks.extend(rc)
        findings.extend(rf)

        cc, cf = self._check_consistency(sources)
        consistency_checks.extend(cc)
        findings.extend(cf)

        sf, sd = self._check_sprint_status(sources)
        findings.extend(sf)
        outdated_docs.extend(sd)

        decision = self._decision(findings)
        status = "ok" if decision == "GO" else "warning"
        recommendations = self._recommendations(findings)
        summary = self._format_summary(request.scope, decision, findings, recommendations)

        provider_name = (request.provider or self._settings.ai.default_provider).strip().lower()
        if provider_name == "ollama":
            try:
                summary = self._ollama_summary(request, findings, summary, sources)
            except AIProviderError as exc:
                warnings.append(str(exc))
                status = "warning"
        elif provider_name == "mock":
            summary = "Read-only documentation audit mode.\n\n" + summary

        metadata = {
            "provider": provider_name,
            "decision": decision,
            "scope": request.scope,
            "source_count": len(sources),
            "prompt_logged": False,
        }
        write_audit(
            event="agent_documentation_audit_run",
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
        return DocumentationAuditResult(
            agent_name=self.agent_name,
            project_name=request.project_name,
            scope=request.scope,
            status=status,
            decision=decision,
            summary=summary,
            findings=findings,
            source_checks=source_checks,
            roadmap_checks=roadmap_checks,
            consistency_checks=consistency_checks,
            recommendations=recommendations,
            missing_docs=missing_docs,
            outdated_docs=outdated_docs,
            sources=sources,
            warnings=warnings,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Source loading (bounded, security-filtered)
    # ------------------------------------------------------------------

    def _load_sources(
        self, request: DocumentationAuditRequest
    ) -> tuple[list[AgentContextSource], list[str]]:
        selected = self._select_files(request.scope, request.max_files)
        sources: list[AgentContextSource] = []
        warnings: list[str] = []
        total_chars = 0

        for path in selected:
            if total_chars >= self._MAX_TOTAL_CONTEXT_CHARS:
                warnings.append(
                    f"Total documentation audit context capped at {self._MAX_TOTAL_CONTEXT_CHARS} chars; "
                    "remaining files skipped."
                )
                break
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                warnings.append(f"Could not read {path.name}: {exc}")
                continue
            allowed = min(request.max_chars_per_file, self._MAX_TOTAL_CONTEXT_CHARS - total_chars)
            trimmed = content[:allowed]
            sources.append(
                AgentContextSource(
                    source_type="documentation-audit-file",
                    label=path.name,
                    path=str(path.resolve()),
                    char_count=len(trimmed),
                    metadata={
                        "scope": request.scope,
                        "truncated": len(content) > len(trimmed),
                        "original_char_count": len(content),
                        "content": trimmed,
                    },
                )
            )
            total_chars += len(trimmed)

        # Add latest v1 audit report path reference for all-light
        if request.scope == "all-light":
            latest = self._latest_v1_audit_report()
            if latest:
                sources.append(
                    AgentContextSource(
                        source_type="report",
                        label=latest.name,
                        path=str(latest.resolve()),
                        char_count=0,
                        metadata={"path_only": True, "content": ""},
                    )
                )

        return sources, warnings

    def _select_files(self, scope: str, max_files: int) -> list[Path]:
        root = get_atlas_root()
        selected: list[Path] = []
        seen: set[Path] = set()
        for pattern in self._SCOPE_PATTERNS[scope]:
            candidate = root / pattern
            if candidate.is_file() and self._is_allowed_path(candidate):
                resolved = candidate.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    selected.append(resolved)
            if len(selected) >= max_files:
                break
        return selected[:max_files]

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

    # ------------------------------------------------------------------
    # Bounded checks
    # ------------------------------------------------------------------

    def _check_source_presence(
        self, request: DocumentationAuditRequest
    ) -> tuple[list[DocumentationSourceCheck], list[DocumentationFinding]]:
        root = get_atlas_root()
        checks: list[DocumentationSourceCheck] = []
        findings: list[DocumentationFinding] = []

        for pattern in self._SCOPE_PATTERNS[request.scope]:
            path = root / pattern
            if path.is_file():
                checks.append(DocumentationSourceCheck(
                    label=path.name,
                    path=str(path.resolve()),
                    status="present",
                    detail="File exists.",
                ))
            else:
                checks.append(DocumentationSourceCheck(
                    label=path.name,
                    path=str(path.resolve()),
                    status="missing",
                    detail="File not found in expected location.",
                ))
                findings.append(DocumentationFinding(
                    severity="medium",
                    category="missing-doc",
                    title=f"Missing documentation file: {path.name}",
                    description=f"Expected documentation file not found: {pattern}",
                    affected_file=str(path.resolve()),
                    evidence="File does not exist at expected path.",
                    recommendation=f"Create {path.name} at {pattern}.",
                ))

        return checks, findings

    def _check_roadmap(
        self, sources: list[AgentContextSource]
    ) -> tuple[list[DocumentationRoadmapCheck], list[DocumentationFinding]]:
        checks: list[DocumentationRoadmapCheck] = []
        findings: list[DocumentationFinding] = []

        content_by_name: dict[str, str] = {
            src.label: src.metadata.get("content", "") for src in sources
        }

        # Sprint 35 should be listed as upcoming/current
        next_sprints_text = content_by_name.get("06-next-sprints.md", "")
        if next_sprints_text:
            sprints_28_34 = ["Sprint 28", "Sprint 29", "Sprint 30", "Sprint 31",
                             "Sprint 32", "Sprint 33", "Sprint 34"]
            for sprint in sprints_28_34:
                if sprint in next_sprints_text:
                    checks.append(DocumentationRoadmapCheck(
                        check_name=f"{sprint} completed",
                        status="pass",
                        detail=f"{sprint} present in next-sprints.md.",
                    ))
                else:
                    checks.append(DocumentationRoadmapCheck(
                        check_name=f"{sprint} completed",
                        status="warn",
                        detail=f"{sprint} not explicitly mentioned in next-sprints.md.",
                    ))

            if "Sprint 35" in next_sprints_text:
                checks.append(DocumentationRoadmapCheck(
                    check_name="Sprint 35 listed",
                    status="pass",
                    detail="Sprint 35 (DocumentationAgent) present in roadmap.",
                ))
            else:
                checks.append(DocumentationRoadmapCheck(
                    check_name="Sprint 35 listed",
                    status="warn",
                    detail="Sprint 35 not found in 06-next-sprints.md.",
                ))
                findings.append(DocumentationFinding(
                    severity="medium",
                    category="roadmap-mismatch",
                    title="Sprint 35 missing from roadmap",
                    description="06-next-sprints.md does not reference Sprint 35 (DocumentationAgent).",
                    affected_file="workspace/knowledge-base/ATLAS/06-next-sprints.md",
                    evidence="'Sprint 35' token not found in file.",
                    recommendation="Update 06-next-sprints.md to reflect Sprint 35 as completed and Sprint 36 as upcoming.",
                ))

            # Check V1/V2/V3 separation
            for scope_label in ("V2", "V3"):
                if scope_label in next_sprints_text:
                    checks.append(DocumentationRoadmapCheck(
                        check_name=f"{scope_label} scope present",
                        status="pass",
                        detail=f"{scope_label} roadmap section found.",
                    ))
                else:
                    checks.append(DocumentationRoadmapCheck(
                        check_name=f"{scope_label} scope present",
                        status="warn",
                        detail=f"{scope_label} roadmap section not found in next-sprints.",
                    ))
        else:
            checks.append(DocumentationRoadmapCheck(
                check_name="roadmap-file",
                status="missing",
                detail="06-next-sprints.md not loaded — skipping roadmap checks.",
            ))

        return checks, findings

    def _check_consistency(
        self, sources: list[AgentContextSource]
    ) -> tuple[list[DocumentationConsistencyCheck], list[DocumentationFinding]]:
        checks: list[DocumentationConsistencyCheck] = []
        findings: list[DocumentationFinding] = []

        content_by_name: dict[str, str] = {
            src.label: src.metadata.get("content", "") for src in sources
        }

        current_status = content_by_name.get("03-current-status.md", "")
        v1_report = content_by_name.get("07-v1-rc-go-report.md", "")

        # Sprint 34 in current-status?
        if current_status:
            if "Sprint 34" in current_status and "SecurityAuditorAgent" in current_status:
                checks.append(DocumentationConsistencyCheck(
                    check_name="Sprint 34 in current-status",
                    status="pass",
                    detail="Sprint 34 SecurityAuditorAgent entry found in 03-current-status.md.",
                ))
            else:
                checks.append(DocumentationConsistencyCheck(
                    check_name="Sprint 34 in current-status",
                    status="warn",
                    detail="Sprint 34/SecurityAuditorAgent not clearly reflected in current-status.",
                ))

            # MainAgent and ToolApprovalAgent referenced?
            for agent_name in ("MainAgent", "ToolApprovalAgent", "SecurityAuditorAgent"):
                if agent_name in current_status:
                    checks.append(DocumentationConsistencyCheck(
                        check_name=f"{agent_name} in current-status",
                        status="pass",
                        detail=f"{agent_name} mentioned in 03-current-status.md.",
                    ))
                else:
                    checks.append(DocumentationConsistencyCheck(
                        check_name=f"{agent_name} in current-status",
                        status="warn",
                        detail=f"{agent_name} not mentioned in 03-current-status.md.",
                    ))
                    findings.append(DocumentationFinding(
                        severity="low",
                        category="outdated-doc",
                        title=f"{agent_name} missing from current-status",
                        description=f"03-current-status.md does not mention {agent_name}.",
                        affected_file="workspace/knowledge-base/ATLAS/03-current-status.md",
                        evidence=f"'{agent_name}' token not found.",
                        recommendation=f"Add {agent_name} entry to current-status after Sprint 35.",
                    ))

        # V1 report consistency
        if v1_report:
            if "Sprint 34" in v1_report and "SecurityAuditorAgent" in v1_report:
                checks.append(DocumentationConsistencyCheck(
                    check_name="Sprint 34 in v1-rc-go-report",
                    status="pass",
                    detail="Sprint 34 referenced in v1-rc-go-report.",
                ))
            else:
                checks.append(DocumentationConsistencyCheck(
                    check_name="Sprint 34 in v1-rc-go-report",
                    status="warn",
                    detail="Sprint 34/SecurityAuditorAgent not found in 07-v1-rc-go-report.",
                ))
                findings.append(DocumentationFinding(
                    severity="medium",
                    category="sprint-status-mismatch",
                    title="Sprint 34 not reflected in V1 RC report",
                    description="07-v1-rc-go-report.md does not reference Sprint 34 SecurityAuditorAgent.",
                    affected_file="workspace/knowledge-base/ATLAS/07-v1-rc-go-report.md",
                    evidence="'Sprint 34' or 'SecurityAuditorAgent' token not found.",
                    recommendation="Update 07-v1-rc-go-report.md to include Sprint 34-35 outcomes.",
                ))

        # NotebookLM workflow doc check
        notebooklm = content_by_name.get("10-notebooklm-workflow.md", "")
        if notebooklm:
            checks.append(DocumentationConsistencyCheck(
                check_name="notebooklm-workflow-doc",
                status="pass",
                detail="10-notebooklm-workflow.md is present and readable.",
            ))
        else:
            checks.append(DocumentationConsistencyCheck(
                check_name="notebooklm-workflow-doc",
                status="missing",
                detail="10-notebooklm-workflow.md not loaded.",
            ))

        return checks, findings

    def _check_sprint_status(
        self, sources: list[AgentContextSource]
    ) -> tuple[list[DocumentationFinding], list[str]]:
        findings: list[DocumentationFinding] = []
        outdated: list[str] = []

        content_by_name: dict[str, str] = {
            src.label: src.metadata.get("content", "") for src in sources
        }

        # Sprint docs 14-21: check each is present in scope
        root = get_atlas_root()
        sprint_docs = {
            "14": "14-sprint-29-memory-agent-projectqa-plan.md",
            "17": "17-sprint-30-planner-agent-plan.md",
            "18": "18-sprint-31-code-reviewer-agent-plan.md",
            "19": "19-sprint-32-tool-approval-design.md",
            "20": "20-sprint-33-main-agent-alpha.md",
            "21": "21-sprint-34-security-auditor-agent.md",
        }
        for doc_num, doc_name in sprint_docs.items():
            path = root / "workspace" / "knowledge-base" / "ATLAS" / doc_name
            if not path.is_file():
                findings.append(DocumentationFinding(
                    severity="medium",
                    category="ai-agent-doc-gap",
                    title=f"Sprint doc missing: {doc_name}",
                    description=f"Agent sprint documentation {doc_name} not found.",
                    affected_file=str(path.resolve()),
                    evidence="File does not exist.",
                    recommendation=f"Create {doc_name} documenting the respective sprint.",
                ))
                outdated.append(doc_name)

        # Sprint 22 (doc 22-sprint-35) should not yet exist (we create it this sprint)
        doc35 = root / "workspace" / "knowledge-base" / "ATLAS" / "22-sprint-35-documentation-agent.md"
        if not doc35.is_file():
            findings.append(DocumentationFinding(
                severity="info",
                category="missing-doc",
                title="22-sprint-35-documentation-agent.md not yet created",
                description="Sprint 35 documentation file does not exist yet.",
                affected_file=str(doc35.resolve()),
                evidence="File does not exist.",
                recommendation="Create 22-sprint-35-documentation-agent.md as part of Sprint 35 completion.",
            ))

        return findings, outdated

    # ------------------------------------------------------------------
    # Decision, recommendations, formatting
    # ------------------------------------------------------------------

    def _decision(self, findings: list[DocumentationFinding]) -> str:
        severities = {item.severity for item in findings}
        if "critical" in severities:
            return "NO-GO"
        if "high" in severities or "medium" in severities:
            return "CONDITIONAL"
        return "GO"

    def _recommendations(
        self, findings: list[DocumentationFinding]
    ) -> list[DocumentationRecommendation]:
        if not findings:
            return [
                DocumentationRecommendation(
                    title="Dokümantasyon tutarlı",
                    text="Kontrol edilen kapsamda kritik eksik veya tutarsızlık bulunmadı.",
                )
            ]
        seen: set[str] = set()
        recs: list[DocumentationRecommendation] = []
        for item in findings:
            if item.recommendation not in seen:
                seen.add(item.recommendation)
                recs.append(DocumentationRecommendation(
                    title=item.title,
                    text=item.recommendation,
                ))
        return recs[:8]

    def _format_summary(
        self,
        scope: str,
        decision: str,
        findings: list[DocumentationFinding],
        recommendations: list[DocumentationRecommendation],
    ) -> str:
        lines = [
            f"Karar: {decision}",
            f"Kapsam: {scope}",
            "",
            "Bulgular:",
        ]
        if findings:
            lines.extend(
                f"- [{item.severity}] {item.category}: {item.title} -> {item.affected_file}"
                for item in findings
            )
        else:
            lines.append("- Kontrol edilen kapsamda kritik dokümantasyon blocker yok.")
        lines.extend(["", "Öneriler:"])
        lines.extend(f"- {rec.title}: {rec.text}" for rec in recommendations)
        lines.extend(["", "Dokümanlar otomatik değiştirilmedi. Uygulama için kullanıcı onayı gereklidir."])
        return "\n".join(lines)

    def _ollama_summary(
        self,
        request: DocumentationAuditRequest,
        findings: list[DocumentationFinding],
        fallback: str,
        sources: list[AgentContextSource],
    ) -> str:
        provider = OllamaAIProvider(self._settings.ai.ollama)
        health = provider.health_check()
        if not health.ok:
            raise AIProviderError(health.message)
        bundle = AIContextBundle(
            project=request.project_name,
            sources=[
                AIContextSource(
                    kind="documentation-audit",
                    label=source.label,
                    path=source.path,
                    content=f"path: {source.path}\nchar_count: {source.char_count}",
                    metadata=dict(source.metadata),
                )
                for source in sources[:8]
            ],
            metadata={
                "total_chars": sum(s.char_count for s in sources),
                "max_total_chars": self._MAX_TOTAL_CONTEXT_CHARS,
            },
        )
        prompt = (
            "Sen DocumentationAgent olarak read-only tavsiye modundasın.\n"
            "Dosya değiştirdiğini iddia etme.\n"
            "Komut çalıştırdığını iddia etme.\n"
            "Dokümantasyon audit sonucunu Türkçe özetle.\n"
            "Deterministik kararı olduğu gibi koru.\n\n"
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
        matches = sorted(
            reports_dir.glob("v1-rc-audit-*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return matches[0] if matches else None
