"""Integration checks (Sprint 14 / 18)."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from app.config.loader import load_project_registry
from app.instructions.generator import check_generated, instruction_check_root
from app.projects import registry as reg


def collect_integration_issues(name: str) -> list[str]:
    """Return human-readable issues; empty list means OK."""
    issues: list[str] = []
    reg_issues = reg.validate_project(name)
    issues.extend(reg_issues)

    project = next((p for p in load_project_registry().projects if p.name == name), None)
    if not project:
        issues.append("unknown project")
        return issues

    base = instruction_check_root(project)

    expected_files = [
        base / "AGENTS.md",
        base / ".github" / "copilot-instructions.md",
        base / ".codex" / "config.toml",
        base / ".cursor" / "rules" / "cursor-project-context.mdc",
    ]
    for p in expected_files:
        if not p.is_file():
            issues.append(f"missing integration file: {p}")

    rules_dir = base / ".cursor" / "rules"
    if not rules_dir.is_dir():
        issues.append(f"missing .cursor/rules directory: {rules_dir}")
    else:
        mdc = list(rules_dir.glob("*.mdc"))
        if not mdc:
            issues.append("no .mdc files under .cursor/rules")

    issues.extend(check_generated(project))
    return issues


def integrations_check(name: str) -> None:
    """Verify Cursor/Copilot/Codex integration files and forbidden-change reflection."""
    console = Console()
    issues = collect_integration_issues(name)
    if issues:
        for issue in issues:
            console.print(f"[red]{issue}[/red]")
        raise typer.Exit(1)
    console.print("[green]integrations check OK[/green]")
