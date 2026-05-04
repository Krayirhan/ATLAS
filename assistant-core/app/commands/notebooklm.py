"""notebooklm import | list | validate"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from app.config.loader import load_project_registry
from app.logging.audit import write_audit
from app.notebooklm.importer import import_summary, validate_kb
from app.paths import get_logs_dir, get_workspace_dir


def _kb_dirs():
    kb = get_workspace_dir() / "knowledge-base"
    if not kb.is_dir():
        return []
    return sorted([p.name for p in kb.iterdir() if p.is_dir()])


def notebooklm_import(
    name: str = typer.Argument(..., help="Project name"),
    source: Path = typer.Option(..., "--source", help="NotebookLM export markdown file"),
) -> None:
    console = Console()
    reg = load_project_registry()
    if not any(p.name == name for p in reg.projects):
        console.print(f"[yellow]Warning: {name} not in project registry (import still runs)[/yellow]")
    log = import_summary(name, source, get_workspace_dir())
    write_audit(
        event="notebooklm_import",
        payload={"project": name, "source": str(source)},
        logs_root=get_logs_dir(),
    )
    console.print(f"[green]Import complete.[/green] Log: {log}")


def notebooklm_list() -> None:
    console = Console()
    for d in _kb_dirs():
        console.print(d)


def notebooklm_validate(name: str) -> None:
    console = Console()
    issues = validate_kb(name, get_workspace_dir())
    if issues:
        for i in issues:
            console.print(f"[red]{i}[/red]")
        raise typer.Exit(1)
    console.print("[green]notebooklm validate OK[/green]")
