"""context build | show-plan"""

from __future__ import annotations

import json
from dataclasses import asdict

import typer
from rich.console import Console

from app.context.builder import build_plan


def _print_plan(project: str, task: str) -> None:
    console = Console()
    plan = build_plan(project, task)
    console.print(json.dumps(asdict(plan), indent=2))


def context_build(project: str, task: str = typer.Option(..., "--task")) -> None:
    _print_plan(project, task)
    from app.logging.audit import write_audit
    from app.paths import get_logs_dir

    write_audit(
        event="context_build",
        payload={"project": project, "task": task},
        logs_root=get_logs_dir(),
    )


def context_show_plan(project: str, task: str = typer.Option(..., "--task")) -> None:
    _print_plan(project, task)
