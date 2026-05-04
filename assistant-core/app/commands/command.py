"""command check / preview for Sprint 11 safe-terminal preview flow."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from app.config.loader import load_project_registry
from app.config.models import ProjectEntry
from app.logging.audit import write_audit
from app.paths import get_logs_dir
from app.safety.command_guard import check_command
from app.safety.policy import get_safety_policy


def command_check(
    project: str = typer.Argument(..., help="Project name (for audit log)"),
    cmd: str = typer.Option(..., "--cmd", help="Command string to evaluate"),
) -> None:
    console = Console()
    reg = load_project_registry()
    item = next((p for p in reg.projects if p.name == project), None)
    if item:
        console.print(f"Suggested working directory (reference): {_resolve_workdir(item)}")
    policy = get_safety_policy()
    result = check_command(cmd, policy)
    write_audit(
        event="command_check",
        payload={"project": project, "cmd": cmd, "result": result},
        logs_root=get_logs_dir(),
    )
    if result["blocked"]:
        console.print("[red]BLOCKED[/red]")
    elif result["approval_required"]:
        console.print("[yellow]APPROVAL REQUIRED[/yellow]")
    else:
        console.print("[green]OK[/green]")
    for r in result["reasons"]:
        console.print(f" - {r}")
    if result["blocked"]:
        raise typer.Exit(2)


def _resolve_workdir(item: ProjectEntry) -> Path:
    cw = str(item.command_workdir or "").strip()
    if cw:
        return Path(cw).resolve()
    return item.root.resolve()


def _project_command(project: str, command_type: str) -> str:
    reg = load_project_registry()
    item = next((p for p in reg.projects if p.name == project), None)
    if not item:
        raise typer.BadParameter(f"Unknown project: {project}")
    key = command_type.strip().lower()
    if key not in {"build", "test", "lint", "status"}:
        raise typer.BadParameter("type must be one of: build, test, lint, status")
    if key == "status":
        cmd = (item.status_command or "").strip() or "git status"
    else:
        raw = getattr(item, f"{key}_command", "") or ""
        cmd = str(raw).strip()
    if not cmd:
        raise typer.BadParameter(f"{project} has no `{key}_command` in registry")
    return cmd


def command_preview(
    project: str = typer.Argument(..., help="Project name from registry"),
    command_type: str = typer.Option(..., "--type", help="build | test | lint | status"),
) -> None:
    """Preview command resolution + safety status, never executes the command."""
    console = Console()
    reg = load_project_registry()
    item = next((p for p in reg.projects if p.name == project), None)
    if not item:
        raise typer.BadParameter(f"Unknown project: {project}")
    cmd = _project_command(project, command_type)
    wd = _resolve_workdir(item)
    policy = get_safety_policy()
    result = check_command(cmd, policy)
    write_audit(
        event="command_preview",
        payload={"project": project, "type": command_type, "cmd": cmd, "result": result},
        logs_root=get_logs_dir(),
    )
    console.print(f"Project: {project}")
    console.print(f"Type: {command_type}")
    console.print("[bold]Preview only - command is not executed.[/bold]")
    console.print(f"Preview: {cmd}")
    console.print(f"Suggested working directory: {wd}")
    if "pytest" in cmd and not (wd / "pyproject.toml").is_file():
        console.print(
            "[yellow]Warning: no pyproject.toml under suggested cwd; "
            "pytest may need the directory that contains pyproject.toml.[/yellow]"
        )
    if result["blocked"]:
        console.print("[red]BLOCKED[/red] (preview only, nothing executed)")
        for r in result["reasons"]:
            console.print(f" - {r}")
        raise typer.Exit(2)
    if result["approval_required"]:
        console.print("[yellow]APPROVAL REQUIRED[/yellow] (preview only, nothing executed)")
    else:
        console.print("[green]SAFE[/green] (preview only, nothing executed)")
    for r in result["reasons"]:
        console.print(f" - {r}")
