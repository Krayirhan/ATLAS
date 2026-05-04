"""instructions preview | generate | check"""

from __future__ import annotations

import typer
from rich.console import Console

from app.config.loader import load_project_registry
from app.instructions import generator as gen
from app.logging.audit import write_audit
from app.paths import get_logs_dir


def _project(name: str):
    reg = load_project_registry()
    for p in reg.projects:
        if p.name == name:
            return p
    raise typer.BadParameter(f"Unknown project: {name}")


def instructions_preview(name: str) -> None:
    console = Console()
    p = _project(name)
    console.print(gen.preview_all(p))


def instructions_generate(name: str) -> None:
    console = Console()
    p = _project(name)
    paths = gen.generate_into_repo(p)
    write_audit(event="instructions_generate", payload={"project": name, "paths": [str(x) for x in paths]}, logs_root=get_logs_dir())
    for path in paths:
        console.print(f"[green]Wrote[/green] {path}")


def instructions_check(name: str) -> None:
    console = Console()
    p = _project(name)
    issues = gen.check_generated(p)
    if issues:
        for i in issues:
            console.print(f"[red]{i}[/red]")
        raise typer.Exit(1)
    console.print("[green]instructions check OK[/green]")
