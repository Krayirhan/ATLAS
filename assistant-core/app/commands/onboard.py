"""onboard command for Sprint 12."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from app.config.loader import ConfigError
from app.config.models import ProjectEntry
from app.instructions.generator import generate_into_repo
from app.logging.audit import write_audit
from app.paths import get_logs_dir, get_workspace_dir
from app.projects import registry as reg


def _knowledge_dir(name: str) -> Path:
    return get_workspace_dir() / "knowledge-base" / name


def _placeholder_kb_files(name: str) -> list[Path]:
    kb = _knowledge_dir(name)
    kb.mkdir(parents=True, exist_ok=True)
    files = [
        "00-project-summary.md",
        "01-architecture-map.md",
        "02-feature-index.md",
        "03-current-status.md",
        "04-risk-list.md",
        "05-release-checklist.md",
        "06-next-sprints.md",
    ]
    written: list[Path] = []
    for fname in files:
        path = kb / fname
        if not path.exists():
            path.write_text(
                f"# {name} - {fname[:-3].replace('-', ' ')}\n\n_Placeholder; refine during onboarding._\n",
                encoding="utf-8",
            )
            written.append(path)
    return written


def onboard_project(
    repo_root: Path = typer.Argument(..., help="Project root path"),
    name: str = typer.Option(..., "--name", help="Project name"),
    project_type: str = typer.Option(..., "--type", help="Project type"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview only, no write"),
    build_command: str = typer.Option("", "--build-command"),
    test_command: str = typer.Option("", "--test-command"),
    lint_command: str = typer.Option("", "--lint-command"),
) -> None:
    console = Console()
    if not repo_root.is_dir():
        console.print(f"[red]Project root not found: {repo_root}[/red]")
        raise typer.Exit(1)
    kb = _knowledge_dir(name)
    entry = ProjectEntry(
        name=name,
        type=project_type,
        root=repo_root.resolve(),
        knowledge=kb.resolve(),
        build_command=build_command,
        test_command=test_command,
        lint_command=lint_command,
        forbidden_changes=[],
    )
    console.print(f"Project: {name}")
    console.print(f"Repo root: {repo_root.resolve()}")
    console.print(f"Knowledge dir: {kb.resolve()}")
    console.print("Planned actions:")
    console.print(" - add project to configs/project-registry.json")
    console.print(" - create knowledge-base placeholder files (00-06)")
    console.print(" - generate instructions into target repo")
    if dry_run:
        console.print("[green]Dry-run complete (no files written).[/green]")
        return
    try:
        reg.add_project(entry)
    except ConfigError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    kb_files = _placeholder_kb_files(name)
    generated = generate_into_repo(entry)
    write_audit(
        event="onboard",
        payload={
            "project": name,
            "repo_root": str(repo_root),
            "knowledge_dir": str(kb),
            "kb_files_created": [str(p) for p in kb_files],
            "instruction_files": [str(p) for p in generated],
        },
        logs_root=get_logs_dir(),
    )
    console.print("[green]Onboard complete.[/green]")
    for p in kb_files:
        console.print(f"KB: {p}")
    for p in generated:
        console.print(f"Instruction: {p}")
