"""Load bounded read-only context for AI queries."""

from __future__ import annotations

from pathlib import Path

from app.ai.models import AIContextBundle, AIContextSource
from app.memory.repository import get_project_status
from app.paths import get_atlas_root, get_memory_db_path, get_workspace_dir
from app.projects.registry import get_project


KB_FILES = (
    "00-project-summary.md",
    "03-current-status.md",
    "04-risk-list.md",
    "05-release-checklist.md",
    "06-next-sprints.md",
    "07-v1-rc-go-report.md",
)
MAX_SOURCE_CHARS = 4000
MAX_TOTAL_CHARS = 12000


class AIContextError(RuntimeError):
    """Context loading error."""


class AIContextLoader:
    def load(self, project_name: str) -> AIContextBundle:
        project = get_project(project_name)
        if not project:
            raise AIContextError(f"Unknown project: {project_name}")

        atlas_root = get_atlas_root().resolve()
        kb_dir = Path(str(project.knowledge)) if project.knowledge else get_workspace_dir() / "knowledge-base" / project_name
        kb_dir = kb_dir.resolve()
        if not self._is_under(atlas_root, kb_dir):
            raise AIContextError(f"Knowledge path is outside ATLAS root: {kb_dir}")

        sources: list[AIContextSource] = [self._load_registry_source(project_name)]
        sources.extend(self._load_memory_sources(project_name))
        for name in KB_FILES:
            path = kb_dir / name
            if path.is_file():
                sources.append(
                    self._file_source(
                        "knowledge-base",
                        path,
                        name,
                        summary_only=name == "07-v1-rc-go-report.md",
                    )
                )
        latest_report = self._latest_system_health_report(project_name)
        if latest_report is not None:
            sources.append(self._file_source("report", latest_report, latest_report.name, summary_only=True))

        bounded_sources = self._apply_total_limit(sources)
        total_chars = sum(int(source.metadata.get("char_count", len(source.content))) for source in bounded_sources)

        return AIContextBundle(
            project=project_name,
            sources=bounded_sources,
            metadata={
                "source_count": len(bounded_sources),
                "knowledge_base": str(kb_dir),
                "max_source_chars": MAX_SOURCE_CHARS,
                "max_total_chars": MAX_TOTAL_CHARS,
                "total_chars": total_chars,
            },
        )

    def _load_registry_source(self, project_name: str) -> AIContextSource:
        from app.config.loader import load_project_registry

        registry = load_project_registry()
        project = next((item for item in registry.projects if item.name == project_name), None)
        if project is None:
            raise AIContextError(f"Unknown project: {project_name}")
        content = "\n".join(
            [
                f"name: {project.name}",
                f"type: {project.type}",
                f"root: {project.root}",
                f"knowledge: {project.knowledge or '(default)'}",
                f"command_workdir: {project.command_workdir or '(project root)'}",
                "forbidden_changes:",
                *[f"- {item}" for item in project.forbidden_changes],
            ]
        )
        return AIContextSource(
            kind="registry",
            label="project-registry",
            path=str((get_atlas_root() / "configs" / "project-registry.json").resolve()),
            content=content[:MAX_SOURCE_CHARS],
            metadata={
                "char_count": min(len(content), MAX_SOURCE_CHARS),
                "source_char_count": len(content),
                "truncated": len(content) > MAX_SOURCE_CHARS,
            },
        )

    def _load_memory_sources(self, project_name: str) -> list[AIContextSource]:
        db_path = get_memory_db_path()
        if not db_path.is_file():
            return []
        status = get_project_status(db_path, project_name)
        return [
            AIContextSource(
                kind="memory",
                label="memory-project-status",
                path=str(db_path.resolve()),
                content=f"project_status: {status}"[:MAX_SOURCE_CHARS],
                metadata={
                    "char_count": min(len(f"project_status: {status}"), MAX_SOURCE_CHARS),
                    "source_char_count": len(f"project_status: {status}"),
                    "truncated": len(f"project_status: {status}") > MAX_SOURCE_CHARS,
                },
            )
        ]

    def _latest_system_health_report(self, project_name: str) -> Path | None:
        reports_dir = get_workspace_dir() / "outputs" / "reports" / project_name
        if not reports_dir.is_dir():
            return None
        matches = sorted(reports_dir.glob("*-system-health.md"), key=lambda path: path.stat().st_mtime, reverse=True)
        return matches[0] if matches else None

    def _file_source(self, kind: str, path: Path, label: str, *, summary_only: bool = False) -> AIContextSource:
        text = path.read_text(encoding="utf-8", errors="replace")
        source_char_count = len(text)
        if summary_only:
            lines = [line.strip() for line in text.splitlines() if line.strip()][:8]
            text = f"path: {path.resolve()}\nsummary:\n" + "\n".join(lines)
        if len(text) > MAX_SOURCE_CHARS:
            text = text[:MAX_SOURCE_CHARS] + "\n...[truncated]..."
        return AIContextSource(
            kind=kind,
            label=label,
            path=str(path.resolve()),
            content=text,
            metadata={
                "truncated": source_char_count > MAX_SOURCE_CHARS or summary_only,
                "char_count": len(text),
                "source_char_count": source_char_count,
                "summary_only": summary_only,
            },
        )

    def _apply_total_limit(self, sources: list[AIContextSource]) -> list[AIContextSource]:
        total = 0
        bounded: list[AIContextSource] = []
        for source in sources:
            char_count = len(source.content)
            remaining = MAX_TOTAL_CHARS - total
            if remaining <= 0:
                break
            if char_count > remaining:
                suffix = "\n...[total limit]..."
                if remaining > len(suffix):
                    clipped = source.content[: remaining - len(suffix)] + suffix
                else:
                    clipped = source.content[:remaining]
                metadata = dict(source.metadata)
                metadata["truncated_total"] = True
                metadata["char_count"] = len(clipped)
                bounded.append(
                    AIContextSource(
                        kind=source.kind,
                        label=source.label,
                        path=source.path,
                        content=clipped,
                        metadata=metadata,
                    )
                )
                total += len(clipped)
                break
            bounded.append(source)
            total += char_count
        return bounded

    @staticmethod
    def _is_under(parent: Path, child: Path) -> bool:
        try:
            child.relative_to(parent)
            return True
        except ValueError:
            return False
