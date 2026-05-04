"""safety show — display policy summary."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from app.safety.policy import get_safety_policy


def safety_show() -> None:
    console = Console()
    p = get_safety_policy()
    t = Table(title="Safety policy")
    t.add_column("Rule set")
    t.add_column("Count / sample")
    t.add_row("allowed_workspace_roots", str(len(p.allowed_workspace_roots)))
    for r in p.allowed_workspace_roots[:3]:
        t.add_row("", r)
    t.add_row("blocked_paths", str(len(p.blocked_paths)))
    t.add_row("blocked_file_patterns", str(len(p.blocked_file_patterns)))
    t.add_row("blocked_commands", str(len(p.blocked_commands)))
    t.add_row("approval_required_commands", str(len(p.approval_required_commands)))
    console.print(t)
