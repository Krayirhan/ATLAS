"""project add | list | show | validate"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from app.config.loader import ConfigError
from app.config.models import ProjectEntry
from app.logging.audit import write_audit
from app.paths import get_configs_dir, get_logs_dir
from app.projects import registry as reg


def project_add(
    name: str,
    project_type: str,
    root: Path,
    knowledge: Optional[Path] = None,
    build_command: str = "",
    test_command: str = "",
    lint_command: str = "",
    forbid: Optional[List[str]] = None,
) -> None:
    console = Console()
    forbid = forbid or []
    entry = ProjectEntry(
        name=name,
        type=project_type,
        root=root,
        knowledge=knowledge if knowledge else "",
        build_command=build_command,
        test_command=test_command,
        lint_command=lint_command,
        forbidden_changes=list(forbid),
    )
    try:
        reg.add_project(entry)
        write_audit(event="project_add", payload={"name": name, "root": str(root)}, logs_root=get_logs_dir())
        console.print(f"[green]Added project {name}[/green]")
    except ConfigError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc


def project_list() -> None:
    from app.config.loader import load_project_registry

    console = Console()
    t = Table(title="Projects")
    t.add_column("Name")
    t.add_column("Type")
    t.add_column("Root")
    for p in load_project_registry().projects:
        t.add_row(p.name, p.type, str(p.root))
    console.print(t)


def project_show(name: str) -> None:
    console = Console()
    p = reg.get_project(name)
    if not p:
        console.print(f"[red]Unknown project: {name}[/red]")
        raise typer.Exit(1)
    console.print(f"Name: {p.name}")
    console.print(f"Type: {p.type}")
    console.print(f"Root: {p.root}")
    console.print(f"Knowledge: {p.knowledge or '(default)'}")
    console.print(f"Build: {p.build_command or '-'}")
    console.print(f"Test: {p.test_command or '-'}")
    console.print(f"Lint: {p.lint_command or '-'}")
    console.print(f"Status: {p.status_command or '-'}")
    console.print(f"Command workdir: {p.command_workdir or '(project root)'}")
    console.print("Forbidden:")
    for f in p.forbidden_changes:
        console.print(f"  - {f}")


def project_validate(name: str) -> None:
    console = Console()
    issues = reg.validate_project(name)
    if issues:
        for i in issues:
            console.print(f"[red]{i}[/red]")
        raise typer.Exit(1)
    console.print("[green]Project validate OK[/green]")
