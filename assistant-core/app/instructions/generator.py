"""Render instruction files from Jinja2 templates."""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape

from app.config.models import ProjectEntry
from app.paths import get_templates_dir


def instruction_check_root(project: ProjectEntry) -> Path:
    """Repo root or assistant-core when AGENTS.md only exists under assistant-core."""
    base = project.root
    ac = project.root / "assistant-core"
    if (ac / "AGENTS.md").is_file() and not (base / "AGENTS.md").is_file():
        return ac
    return base


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(get_templates_dir())),
        autoescape=select_autoescape(enabled_extensions=()),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _template_name(project: ProjectEntry, filename: str) -> str:
    """Prefer templates/by-type/<type>/<file> when present (Sprint 21)."""
    rel_path = Path("by-type") / project.type / filename
    candidate = get_templates_dir() / rel_path
    if candidate.is_file():
        return rel_path.as_posix()
    return filename


def _render_named(project: ProjectEntry, filename: str) -> str:
    env = _env()
    name = _template_name(project, filename)
    try:
        return env.get_template(name).render(**_ctx(project))
    except TemplateNotFound as exc:
        raise TemplateNotFound(name) from exc


def _ctx(project: ProjectEntry) -> Dict[str, object]:
    knowledge = str(project.knowledge) if project.knowledge else ""
    return {
        "project_name": project.name,
        "project_type": project.type,
        "project_root": str(project.root.resolve()),
        "knowledge_path": knowledge,
        "forbidden_changes": project.forbidden_changes,
    }


def render_agents(project: ProjectEntry) -> str:
    return _render_named(project, "AGENTS.md.j2")


def render_copilot(project: ProjectEntry) -> str:
    return _render_named(project, "copilot-instructions.md.j2")


def render_cursor_mdc(project: ProjectEntry) -> str:
    return _render_named(project, "cursor-project-context.mdc.j2")


def render_codex_toml(project: ProjectEntry) -> str:
    return _render_named(project, "codex-config.toml.j2")


def preview_all(project: ProjectEntry) -> str:
    parts = [
        "=== AGENTS.md ===\n" + render_agents(project),
        "=== .github/copilot-instructions.md ===\n" + render_copilot(project),
        "=== .cursor/rules/cursor-project-context.mdc ===\n" + render_cursor_mdc(project),
        "=== .codex/config.toml ===\n" + render_codex_toml(project),
    ]
    return "\n\n".join(parts)


def _backup_if_exists(path: Path) -> None:
    if path.is_file():
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy2(path, path.with_suffix(path.suffix + f".bak.{ts}"))


def generate_into_repo(project: ProjectEntry) -> list[Path]:
    root = instruction_check_root(project)
    written: list[Path] = []
    pairs = [
        (root / "AGENTS.md", render_agents(project)),
        (root / ".github" / "copilot-instructions.md", render_copilot(project)),
        (root / ".cursor" / "rules" / "cursor-project-context.mdc", render_cursor_mdc(project)),
        (root / ".codex" / "config.toml", render_codex_toml(project)),
    ]
    for path, content in pairs:
        path.parent.mkdir(parents=True, exist_ok=True)
        _backup_if_exists(path)
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def check_generated(project: ProjectEntry) -> list[str]:
    issues: list[str] = []
    base = instruction_check_root(project)
    checks = [
        base / "AGENTS.md",
        base / ".github" / "copilot-instructions.md",
        base / ".cursor" / "rules" / "cursor-project-context.mdc",
        base / ".codex" / "config.toml",
    ]
    texts: list[str] = []
    for p in checks:
        if not p.is_file():
            issues.append(f"missing: {p}")
        else:
            texts.append(p.read_text(encoding="utf-8", errors="replace"))
    blob = "\n".join(texts).lower()
    for line in project.forbidden_changes:
        if line and line.strip().lower() not in blob:
            issues.append(f"forbidden change not found in generated instructions: {line}")
    return issues
