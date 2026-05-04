"""doctor — environment and layout checks (Sprint 20 full doctor)."""

from __future__ import annotations

import platform
import subprocess
import sys
import uuid
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from app.config.loader import ConfigError, load_and_validate_configs, load_project_registry, load_safety_policy
from app.instructions.generator import instruction_check_root
from app.paths import (
    get_atlas_root,
    get_configs_dir,
    get_logs_dir,
    get_memory_db_path,
    get_templates_dir,
    get_workspace_dir,
)


def _sh(cmd: str, timeout: float = 20.0) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = (proc.stdout or proc.stderr or "").strip()
        line = out.splitlines()[0] if out else "(no output)"
        return proc.returncode == 0, line[:240]
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)[:240]


def doctor(full: bool = typer.Option(False, help="Run extended checks (Sprint 20)")) -> None:
    console = Console()
    table = Table(title="ATLAS doctor" + (" - full" if full else ""))
    table.add_column("Check")
    table.add_column("Status")

    critical_fail = False
    soft_warn = False

    pyver = sys.version_info
    ok_py = pyver >= (3, 10)
    table.add_row("Python >= 3.10", "ok" if ok_py else f"fail: {sys.version}")
    if not ok_py:
        critical_fail = True

    root = get_atlas_root()
    table.add_row("ATLAS root", str(root))

    for label, path in [
        ("assistant-core", root / "assistant-core"),
        ("workspace", get_workspace_dir()),
        ("configs", get_configs_dir()),
        ("logs", get_logs_dir()),
        ("templates", get_templates_dir()),
        ("mcp-servers", root / "mcp-servers"),
        ("workspace/memory", get_workspace_dir() / "memory"),
        ("workspace/knowledge-base", get_workspace_dir() / "knowledge-base"),
        ("workspace/outputs", get_workspace_dir() / "outputs"),
        ("workspace/notebooklm-exports", get_workspace_dir() / "notebooklm-exports"),
        ("backups", root / "backups"),
    ]:
        ok = path.is_dir()
        table.add_row(label, "ok" if ok else f"fail: missing {path}")
        if not ok:
            critical_fail = True

    try:
        load_and_validate_configs()
        table.add_row("config validate", "ok")
    except ConfigError as exc:
        table.add_row("config validate", f"fail: {exc}")
        critical_fail = True

    try:
        pol = load_safety_policy()
        n_blk = len(pol.blocked_commands)
        table.add_row("safety policy", f"ok ({n_blk} blocked command tokens)")
        if n_blk == 0:
            table.add_row("safety policy depth", "warn: no blocked_commands")
            soft_warn = True
    except ConfigError as exc:
        table.add_row("safety policy", f"fail: {exc}")
        critical_fail = True

    log_probe = get_logs_dir() / "tool-calls" / f".doctor-write-{uuid.uuid4().hex}.tmp"
    try:
        log_probe.parent.mkdir(parents=True, exist_ok=True)
        log_probe.write_text("ok\n", encoding="utf-8")
        log_probe.unlink(missing_ok=True)
        table.add_row("logs writable", "ok")
    except OSError as exc:
        table.add_row("logs writable", f"fail: {exc}")
        critical_fail = True

    if full:
        table.add_row("platform", platform.platform())

        for label, cmd in [
            ("node", "node --version"),
            ("npm", "npm --version"),
            ("git", "git --version"),
            ("docker", "docker --version"),
        ]:
            ok, line = _sh(cmd)
            if ok:
                table.add_row(label, f"ok ({line})")
            else:
                table.add_row(label, f"warn: {line}")
                soft_warn = True

        gen_dir = get_configs_dir() / "generated"
        for fname in ("cursor.mcp.json", "vscode.mcp.json", "codex.config.toml"):
            p = gen_dir / fname
            ok = p.is_file()
            table.add_row(f"generated/{fname}", "ok" if ok else "warn: run mcp generate")
            if not ok:
                soft_warn = True

        mem = get_memory_db_path()
        table.add_row("SQLite memory DB", "ok" if mem.is_file() else "warn: run memory init")
        if not mem.is_file():
            soft_warn = True

        try:
            reg = load_project_registry()
            for proj in reg.projects:
                kb = Path(str(proj.knowledge)) if proj.knowledge else get_workspace_dir() / "knowledge-base" / proj.name
                kb_ok = kb.is_dir()
                table.add_row(f"KB dir ({proj.name})", "ok" if kb_ok else f"warn: {kb}")
                if not kb_ok:
                    soft_warn = True
                ag = instruction_check_root(proj) / "AGENTS.md"
                table.add_row(f"AGENTS.md ({proj.name})", "ok" if ag.is_file() else "warn: run instructions generate")
                if not ag.is_file():
                    soft_warn = True
        except ConfigError as exc:
            table.add_row("registry scan (full)", f"fail: {exc}")
            critical_fail = True

    console.print(table)

    if full and soft_warn and not critical_fail:
        console.print("[yellow]Completed with warnings (see table).[/yellow]")
    if critical_fail:
        console.print("[red]Doctor finished with failures.[/red]")
        raise typer.Exit(code=1)
