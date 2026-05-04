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


def _optional_tooling_issue(msg: str) -> bool:
    """Copilot/Codex/Cursor files missing are optional when AGENTS.md exists (Sprint 27)."""
    m = msg.lower()
    if "missing integration file:" in m:
        return any(x in m for x in (".github", ".codex", ".cursor"))
    if "missing .cursor/rules directory" in m or "no .mdc files under" in m:
        return True
    return False


def partition_integration_issues(name: str) -> tuple[list[str], list[str]]:
    """Split issues into (critical, optional). Optional is non-blocking for `integrations check`."""
    issues = collect_integration_issues(name)
    project = next((p for p in load_project_registry().projects if p.name == name), None)
    if not project:
        return issues, []
    base = instruction_check_root(project)
    has_agents = (base / "AGENTS.md").is_file()
    critical: list[str] = []
    optional: list[str] = []
    for msg in issues:
        if has_agents and _optional_tooling_issue(msg):
            optional.append(msg)
        else:
            critical.append(msg)
    return critical, optional


def integrations_check(name: str) -> None:
    """Verify integration files; critical failures exit 1, optional gaps print as warnings only."""
    console = Console()
    critical, optional = partition_integration_issues(name)
    for msg in optional:
        console.print(f"[yellow]{msg}[/yellow]")
    if critical:
        for issue in critical:
            console.print(f"[red]{issue}[/red]")
        raise typer.Exit(1)
    console.print("[green]integrations check OK[/green]")
