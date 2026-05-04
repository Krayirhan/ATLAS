"""memory init | sync-projects | project-status | add-decision | list-decisions"""

from __future__ import annotations

import typer
from rich.console import Console

from app.logging.audit import write_audit
from app.memory.db import init_db
from app.memory.repository import (
    add_decision,
    get_project_status,
    list_decisions,
    set_project_status,
    sync_projects_from_registry,
)
from app.paths import get_logs_dir, get_memory_db_path


def memory_init() -> None:
    db = get_memory_db_path()
    init_db(db)
    write_audit(event="memory_init", payload={"db": str(db)}, logs_root=get_logs_dir())
    Console().print(f"[green]Initialized[/green] {db}")


def memory_sync_projects() -> None:
    db = get_memory_db_path()
    added, updated = sync_projects_from_registry(db)
    write_audit(
        event="memory_sync_projects",
        payload={"added": added, "updated": updated},
        logs_root=get_logs_dir(),
    )
    Console().print(f"[green]Sync complete[/green]: added={added}, updated={updated}")


def memory_project_status(
    name: str,
    new_status: str | None = typer.Option(None, "--set", help="Set status text in memory"),
) -> None:
    console = Console()
    db = get_memory_db_path()
    if not db.is_file():
        console.print("[red]Run memory init first[/red]")
        raise typer.Exit(1)
    if new_status is not None:
        set_project_status(db, name, new_status)
        console.print("[green]Status updated[/green]")
    else:
        console.print(get_project_status(db, name))


def memory_add_decision(name: str, title: str = typer.Option(..., "--title"), body: str = typer.Option(..., "--body")) -> None:
    db = get_memory_db_path()
    if not db.is_file():
        Console().print("[red]Run memory init first[/red]")
        raise typer.Exit(1)
    try:
        add_decision(db, name, title, body)
    except ValueError as exc:
        Console().print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    write_audit(event="memory_add_decision", payload={"project": name, "title": title}, logs_root=get_logs_dir())
    Console().print("[green]Decision saved[/green]")


def memory_list_decisions(name: str) -> None:
    console = Console()
    db = get_memory_db_path()
    if not db.is_file():
        console.print("[red]Run memory init first[/red]")
        raise typer.Exit(1)
    rows = list_decisions(db, name)
    if not rows:
        console.print("(no decisions)")
        return
    for title, body in rows:
        console.print(f"[bold]{title}[/bold]\n{body}\n")
