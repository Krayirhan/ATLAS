"""logs list / logs show / logs project."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from app.logging.audit import _scrub
from app.paths import get_logs_dir


def logs_list() -> None:
    console = Console()
    root = get_logs_dir()
    if not root.is_dir():
        console.print("[yellow]No logs directory yet.[/yellow]")
        return
    for sub in sorted(root.iterdir()):
        if sub.is_dir():
            files = sorted(sub.glob("*.jsonl"))
            console.print(f"[bold]{sub.name}[/bold] ({len(files)} files)")


def logs_show(last: int = typer.Option(10, "--last", help="Last N lines across recent files")) -> None:
    console = Console()
    root = get_logs_dir()
    lines: list[str] = []
    for sub in sorted(root.iterdir(), reverse=True):
        if not sub.is_dir():
            continue
        for f in sorted(sub.glob("*.jsonl"), reverse=True):
            lines.extend(f.read_text(encoding="utf-8").splitlines())
            if len(lines) >= last:
                break
        if len(lines) >= last:
            break
    for ln in lines[-last:]:
        console.print(ln)


def _record_matches_project(rec: dict, project: str) -> bool:
    want = project.strip()
    if not want:
        return False
    for key in ("project", "project_name", "name"):
        v = rec.get(key)
        if isinstance(v, str) and v.strip() == want:
            return True
    payload = rec.get("payload")
    if isinstance(payload, dict):
        for key in ("project", "name"):
            v = payload.get(key)
            if isinstance(v, str) and v.strip() == want:
                return True
    return False


def logs_project(project: str, last: int = 10) -> None:
    """Filter JSONL audit lines by project name (read-only)."""
    console = Console()
    root = get_logs_dir()
    if not root.is_dir():
        console.print("[yellow]No logs directory yet.[/yellow]")
        return

    jsonl_files: list[Path] = []
    for sub in ("tool-calls", "sessions", "errors"):
        d = root / sub
        if d.is_dir():
            jsonl_files.extend(d.glob("*.jsonl"))

    jsonl_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    matches: list[tuple[str, dict]] = []
    for fp in jsonl_files:
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            console.print(f"[yellow]Could not read {fp}: {exc}[/yellow]")
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                console.print(f"[yellow]Skipping invalid JSONL {fp.name}:{line_no}[/yellow]")
                continue
            if not isinstance(rec, dict):
                continue
            if _record_matches_project(rec, project):
                ts = str(rec.get("ts") or "")
                matches.append((ts, rec))

    matches.sort(key=lambda x: x[0])
    slice_ = matches[-last:] if last > 0 else []
    if not slice_:
        console.print(f"(no log lines matched project {project!r})")
        return
    for _, rec in slice_:
        console.print(json.dumps(_scrub(rec), ensure_ascii=False), markup=False, highlight=False)
