"""CLI commands for MCP config generation."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from app.config.loader import ConfigError
from app.mcp.generator import generate_all, list_servers, plan_mcp_generate
from app.paths import get_atlas_root


def mcp_list_cmd() -> None:
    console = Console()
    try:
        for name in list_servers():
            console.print(name)
    except ConfigError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc


def mcp_generate_cmd(
    target: str | None = typer.Option(
        None,
        "--target",
        help="cursor | vscode | codex | all (default: all)",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show planned files and content preview; write nothing"),
) -> None:
    console = Console()
    try:
        if dry_run:
            planned = plan_mcp_generate(target=target or "all")
            console.print("[bold]Dry-run - no files written (exit 0).[/bold]")
            for path, content in planned:
                console.print(f"Would write: {path} ({len(content)} bytes)")
                preview = content if len(content) <= 3500 else content[:3500] + "\n... [truncated] ...\n"
                console.print(preview)
            return
        outputs = generate_all(target=target or "all")
    except (ConfigError, ValueError) as exc:
        console.print(f"[red]MCP generation failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    for output in outputs:
        console.print(f"Generated: {output}")


def _default_install_destination(target: str, project: str | None = None) -> str:
    root = get_atlas_root()
    t = target.lower().strip()
    if t == "cursor":
        return str(root / ".cursor" / "mcp.json")
    if t == "codex":
        return str(root / ".codex" / "config.toml")
    if t == "vscode":
        if project:
            return f"<project:{project}>/.vscode/mcp.json"
        return "<project-root>/.vscode/mcp.json"
    raise ValueError(f"Unknown MCP install target: {target}")


def mcp_install_cmd(
    target: str = typer.Option(..., "--target", help="cursor | vscode | codex"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show plan without writing"),
    project: str | None = typer.Option(None, "--project", help="Only for vscode destination preview"),
) -> None:
    """
    Sprint 13 helper:
    - always generates latest target file
    - dry-run prints destination + backup/no-overwrite policy
    - non-dry-run writes only if destination does not exist
    """
    console = Console()
    t = target.lower().strip()
    if t not in {"cursor", "vscode", "codex"}:
        console.print("[red]target must be cursor | vscode | codex[/red]")
        raise typer.Exit(1)
    try:
        outputs = generate_all(target=t)
    except (ConfigError, ValueError) as exc:
        console.print(f"[red]MCP install failed:[/red] {exc}")
        raise typer.Exit(1) from exc
    src = outputs[0]
    dst = _default_install_destination(t, project=project)
    console.print(f"Source: {src}")
    console.print(f"Destination: {dst}")
    console.print("Policy: no-overwrite; if destination exists keep it untouched.")
    console.print("Backup plan: if manual replace is needed, copy destination to *.bak.<timestamp> first.")
    if dry_run:
        console.print("[green]Dry-run complete (no files written).[/green]")
        return
    # Conservative implementation for V1: install only into repo-local tool config if absent.
    if dst.startswith("<project"):
        console.print("[yellow]VSCode install requires explicit project path handling; use --dry-run.[/yellow]")
        raise typer.Exit(1)
    if t == "vscode":
        console.print("[yellow]VSCode install path is project-specific; use --dry-run preview.[/yellow]")
        raise typer.Exit(1)
    dst_path = Path(dst).resolve()
    if dst_path.exists():
        console.print(f"[yellow]Skipped (exists): {dst_path}[/yellow]")
        return
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    dst_path.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    console.print(f"[green]Installed[/green] {dst_path}")
