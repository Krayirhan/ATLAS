"""MemoryAgent: build a safe read-only project snapshot."""

from __future__ import annotations

from pathlib import Path

from app.agents.base import BaseAgent
from app.agents.models import AgentContextSource, AgentRunRequest, AgentRunResult, MemorySnapshot
from app.ai.context_loader import AIContextError, AIContextLoader
from app.logging.audit import write_audit
from app.memory.repository import list_decisions
from app.paths import get_logs_dir, get_memory_db_path, get_workspace_dir
from app.projects.registry import get_project


class MemoryAgent(BaseAgent):
    agent_name = "memory-agent"

    def __init__(self, *, context_loader: AIContextLoader | None = None) -> None:
        self._context_loader = context_loader or AIContextLoader()

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        snapshot = self.snapshot(request.project_name)
        write_audit(
            event="agent_memory_run",
            payload={
                "agent_name": self.agent_name,
                "project": request.project_name,
                "source_count": len(snapshot.context_sources),
            },
            logs_root=get_logs_dir(),
            stream="tool-calls",
        )
        answer = self._format_snapshot(snapshot)
        return AgentRunResult(
            agent_name=self.agent_name,
            project_name=request.project_name,
            status="ok" if not snapshot.warnings else "warning",
            answer=answer,
            sources=snapshot.context_sources,
            warnings=snapshot.warnings,
            metadata={"source_count": len(snapshot.context_sources)},
        )

    def snapshot(self, project_name: str) -> MemorySnapshot:
        project = get_project(project_name)
        if not project:
            raise AIContextError(f"Unknown project: {project_name}")

        bundle = self._context_loader.load(project_name)
        warnings: list[str] = []
        recent_reports: list[str] = []
        sources = [self._to_agent_source(source) for source in bundle.sources]

        status_source = self._find(bundle, "03-current-status.md")
        risks_source = self._find(bundle, "04-risk-list.md")
        next_source = self._find(bundle, "06-next-sprints.md")
        release_source = self._find(bundle, "07-v1-rc-go-report.md")

        latest_audit = self._latest_v1_audit_report()
        if latest_audit is not None:
            recent_reports.append(str(latest_audit.resolve()))
            sources.append(self._path_only_source("report", latest_audit.name, latest_audit))
        else:
            warnings.append("Latest V1 audit report not found.")

        latest_system = next((s for s in bundle.sources if s.kind == "report"), None)
        if latest_system is not None:
            recent_reports.append(latest_system.path)
        else:
            warnings.append("Latest system-health report not found.")

        decisions: list[tuple[str, str]] = []
        db_path = get_memory_db_path()
        if db_path.is_file():
            decisions = list_decisions(db_path, project_name)
        else:
            warnings.append("Memory DB not found.")

        return MemorySnapshot(
            project_name=project_name,
            project_type=project.type,
            root=str(project.root),
            knowledge_path=str(project.knowledge),
            current_status=status_source.content if status_source else "knowledge-base icinde bu bilgi yok",
            risks=risks_source.content if risks_source else "knowledge-base icinde bu bilgi yok",
            next_sprints=next_source.content if next_source else "knowledge-base icinde bu bilgi yok",
            release_status=release_source.content if release_source else "knowledge-base icinde bu bilgi yok",
            recent_reports=recent_reports,
            decisions=decisions,
            context_sources=sources,
            warnings=warnings,
        )

    def _latest_v1_audit_report(self) -> Path | None:
        reports_dir = get_workspace_dir() / "outputs" / "reports" / "V1"
        if not reports_dir.is_dir():
            return None
        matches = sorted(reports_dir.glob("v1-rc-audit-*.md"), key=lambda path: path.stat().st_mtime, reverse=True)
        return matches[0] if matches else None

    def _find(self, bundle, label: str):
        return next((source for source in bundle.sources if source.label == label), None)

    def _to_agent_source(self, source) -> AgentContextSource:
        return AgentContextSource(
            source_type=source.kind,
            label=source.label,
            path=source.path,
            char_count=int(source.metadata.get("char_count", len(source.content))),
            metadata=dict(source.metadata),
        )

    def _path_only_source(self, source_type: str, label: str, path: Path) -> AgentContextSource:
        return AgentContextSource(
            source_type=source_type,
            label=label,
            path=str(path.resolve()),
            char_count=0,
            metadata={"path_only": True},
        )

    def _format_snapshot(self, snapshot: MemorySnapshot) -> str:
        lines = [
            f"Project: {snapshot.project_name}",
            f"Type: {snapshot.project_type}",
            f"Root: {snapshot.root}",
            f"Knowledge: {snapshot.knowledge_path}",
            "",
            "Current status:",
            snapshot.current_status[:800],
            "",
            "Recent reports:",
        ]
        if snapshot.recent_reports:
            lines.extend(f"- {item}" for item in snapshot.recent_reports)
        else:
            lines.append("- (none)")
        if snapshot.warnings:
            lines.extend(["", "Warnings:", *[f"- {item}" for item in snapshot.warnings]])
        return "\n".join(lines)
