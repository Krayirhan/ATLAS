"""Split NotebookLM-style markdown into knowledge-base files."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple


def _split_sections(text: str) -> List[Tuple[str, str]]:
    """Return list of (heading, body) from markdown # headings."""
    lines = text.splitlines()
    sections: List[Tuple[str, str]] = []
    current_title = "Introduction"
    current: list[str] = []
    heading_re = re.compile(r"^(#{1,3})\s+(.*)$")
    for line in lines:
        m = heading_re.match(line)
        if m:
            if current:
                sections.append((current_title, "\n".join(current).strip()))
            current_title = m.group(2).strip()
            current = []
        else:
            current.append(line)
    if current or sections:
        sections.append((current_title, "\n".join(current).strip()))
    return sections


def _bucket_file(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ("summary", "overview", "project")):
        return "00-project-summary.md"
    if "architect" in t or "structure" in t or "stack" in t:
        return "01-architecture-map.md"
    if "feature" in t or "module" in t:
        return "02-feature-index.md"
    if "status" in t or "current" in t or "progress" in t:
        return "03-current-status.md"
    if "risk" in t or "issue" in t:
        return "04-risk-list.md"
    if "release" in t or "checklist" in t:
        return "05-release-checklist.md"
    if "next" in t or "sprint" in t or "roadmap" in t:
        return "06-next-sprints.md"
    return "03-current-status.md"


EXPECTED_FILES = [
    "00-project-summary.md",
    "01-architecture-map.md",
    "02-feature-index.md",
    "03-current-status.md",
    "04-risk-list.md",
    "05-release-checklist.md",
    "06-next-sprints.md",
    "07-notebooklm-import-log.md",
]


def import_summary(project_name: str, source: Path, workspace: Path) -> Path:
    if not source.is_file():
        raise FileNotFoundError(str(source))
    kb = workspace / "knowledge-base" / project_name
    kb.mkdir(parents=True, exist_ok=True)
    text = source.read_text(encoding="utf-8")
    sections = _split_sections(text)
    chunks_by_file: dict[str, list[str]] = {f: [] for f in EXPECTED_FILES if f != "07-notebooklm-import-log.md"}
    for title, body in sections:
        fname = _bucket_file(title)
        if fname not in chunks_by_file:
            fname = "03-current-status.md"
        chunks_by_file[fname].append(f"## {title}\n\n{body}".strip())
    for fname in chunks_by_file:
        content = f"# {project_name} — {fname[:-3].replace('-', ' ')}\n\n"
        parts = chunks_by_file[fname]
        content += "\n\n---\n\n".join(parts) if parts else "_Imported placeholder; refine manually._\n"
        (kb / fname).write_text(content + "\n", encoding="utf-8")
    log = kb / "07-notebooklm-import-log.md"
    log.write_text(
        "\n".join(
            [
                f"# NotebookLM import log — {project_name}",
                "",
                f"- Imported at (UTC): {datetime.now(timezone.utc).isoformat()}",
                f"- Source: `{source}`",
                f"- Sections parsed: {len(sections)}",
                "",
                "Review ambiguous content in `03-current-status.md` and split manually if needed.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return log


def validate_kb(project_name: str, workspace: Path) -> list[str]:
    kb = workspace / "knowledge-base" / project_name
    issues: list[str] = []
    if not kb.is_dir():
        issues.append(f"missing knowledge dir: {kb}")
        return issues
    for name in EXPECTED_FILES:
        if not (kb / name).is_file():
            issues.append(f"missing {name}")
    return issues
