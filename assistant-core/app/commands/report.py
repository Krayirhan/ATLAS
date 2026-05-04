"""Report generator (Sprint 19)."""

from __future__ import annotations

import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from app.commands.integrations import collect_integration_issues
from app.config.loader import ConfigError, load_and_validate_configs, load_project_registry, load_safety_policy
from app.logging.audit import write_audit
from app.memory.repository import (
    add_analysis_report,
    latest_analysis_report,
    list_analysis_reports,
    sync_projects_from_registry,
)
from app.paths import get_configs_dir, get_logs_dir, get_memory_db_path, get_workspace_dir


REPORT_TYPES = frozenset(
    {
        "project-review",
        "release-audit",
        "v1-rc-audit",
        "sprint-plan",
        "code-review",
        "integration-check",
        "notebooklm-import",
        "mcp-status",
        "system-health",
    }
)


def _ensure_project(name: str):
    reg = load_project_registry()
    p = next((x for x in reg.projects if x.name == name), None)
    if not p:
        raise typer.BadParameter(f"Unknown project: {name}")
    return p


def _report_path(project: str, report_type: str) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = get_workspace_dir() / "outputs" / "reports" / project
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{ts}-{report_type}.md"


def _kb_path(p, project_name: str) -> Path:
    return Path(str(p.knowledge)) if p.knowledge else get_workspace_dir() / "knowledge-base" / project_name


def _common_status_block(project_name: str, p) -> list[str]:
    kb = _kb_path(p, project_name)
    lines: list[str] = [
        "## Project name",
        "",
        f"- **{project_name}**",
        "",
        "## Root path",
        "",
        f"- `{p.root}`",
        "",
        "## Knowledge base path",
        "",
        f"- `{kb}`",
        "",
        "## Config status",
        "",
    ]
    try:
        load_and_validate_configs()
        lines.append("- **OK** — settings, registry, safety, and MCP master validate.")
    except ConfigError as exc:
        lines.append(f"- **FAIL** — {exc}")
    lines.extend(["", "## Safety status", ""])
    try:
        pol = load_safety_policy()
        lines.append(
            f"- Policy loaded: **OK** "
            f"({len(pol.blocked_commands)} blocked commands, "
            f"{len(pol.approval_required_commands)} approval-required, "
            f"{len(pol.blocked_file_patterns)} file patterns)."
        )
    except ConfigError as exc:
        lines.append(f"- **FAIL** — {exc}")
    lines.extend(["", "## Registry status", ""])
    try:
        reg = load_project_registry()
        names = [x.name for x in reg.projects]
        lines.append(f"- Projects: {', '.join(names) if names else '(none)'}")
    except ConfigError as exc:
        lines.append(f"- **FAIL** — {exc}")
    lines.extend(["", "## MCP status", ""])
    gen = get_configs_dir() / "generated"
    for fname in ("cursor.mcp.json", "vscode.mcp.json", "codex.config.toml"):
        fp = gen / fname
        lines.append(f"- `{fp.name}`: {'present' if fp.is_file() else 'missing'}")
    lines.extend(["", "## Memory status", ""])
    db = get_memory_db_path()
    lines.append(f"- DB path: `{db}` — {'present' if db.is_file() else 'missing (run memory init)'}")
    lines.extend(["", "## Context status", ""])
    ctx = get_workspace_dir() / "context"
    lines.append(f"- Workspace context dir exists: **{ctx.is_dir()}** (`{ctx}`)")
    lines.extend(["", "## Logs status", ""])
    logs = get_logs_dir()
    lines.append(f"- Logs root exists: **{logs.is_dir()}** (`{logs}`)")
    lines.extend(["", "## Doctor status", ""])
    lines.append("- Run `python -m app.cli doctor` and `doctor --full` locally for live checks.")
    lines.extend(["", "## Test status", ""])
    lines.append("- Run `python -m pytest -q` from `assistant-core` for authoritative test results.")
    lines.extend(["", "## Known warnings", ""])
    lines.append("- Optional tools (node, npm, git, docker) may be absent; `doctor --full` surfaces those as warnings only.")
    lines.extend(["", "## Security risks", ""])
    lines.append(
        "- MCP helper scripts are not full stdio MCP servers; treat as local helpers only.\n"
        "- Do not enable full-disk MCP or unrestricted terminal execution in V1."
    )
    lines.extend(["", "## Next actions", ""])
    lines.append(
        "- Keep `workspace-filesystem` scoped to the ATLAS workspace only.\n"
        "- Re-run `mcp generate` after changing `mcp.master.json`.\n"
        "- Sync memory after registry edits: `memory sync-projects`."
    )
    return lines


def _verdict_from_config() -> str:
    try:
        load_and_validate_configs()
        return "GO"
    except ConfigError:
        return "NO-GO"


def _body(project_name: str, report_type: str) -> str:
    p = _ensure_project(project_name)
    lines = [
        f"# ATLAS report — {report_type}",
        "",
        f"- Project: **{project_name}**",
        f"- Type: `{report_type}`",
        f"- Generated (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"- Root: `{p.root}`",
        "",
    ]
    depth_types = {
        "system-health",
        "integration-check",
        "project-review",
        "v1-rc-audit",
        "mcp-status",
    }
    if report_type in depth_types:
        lines.extend(_common_status_block(project_name, p))

    if report_type == "integration-check":
        issues = collect_integration_issues(project_name)
        lines.extend(["", "## Integration check detail", ""])
        if issues:
            lines.append("**Status:** FAIL")
            for i in issues:
                lines.append(f"- {i}")
        else:
            lines.append("**Status:** OK")
        lines.append("")
    elif report_type == "mcp-status":
        lines.extend(["", "## MCP master", ""])
        lines.append("- Validated during `config validate` (workspace-filesystem path must match ATLAS workspace).")
        lines.append("")
    elif report_type == "system-health":
        lines.extend(["", "## Runtime", ""])
        lines.append(f"- Python: `{sys.version.split()[0]}` on `{platform.system()}`")
        lines.append("")
    elif report_type == "project-review":
        lines.extend(["", "## Project review", ""])
        lines.append(f"- Type: `{p.type}`")
        lines.append(f"- Test command: `{p.test_command or '-'}`")
        lines.append(f"- Build command: `{p.build_command or '-'}`")
        lines.append(f"- Command workdir: `{p.command_workdir or '(project root)'}`")
        lines.append("")
    elif report_type == "v1-rc-audit":
        lines.extend(["", "## V1 RC audit", ""])
        lines.append("- See also `python -m app.cli audit v1-rc` for checklist markdown under `workspace/outputs/reports/V1/`.")
        lines.append("")
    elif report_type == "notebooklm-import":
        kb = _kb_path(p, project_name)
        logf = kb / "07-notebooklm-import-log.md"
        lines.append("## NotebookLM import")
        lines.append("")
        lines.append(f"- Knowledge dir: `{kb}`")
        lines.append(f"- Import log present: **{logf.is_file()}**")
        lines.append("")
    elif report_type not in depth_types:
        lines.append("## Summary")
        lines.append("")
        lines.append("_Auto-generated outline; extend manually as needed._")
        lines.append("")
        lines.append(f"- Project type: `{p.type}`")
        lines.append("")

    if report_type in depth_types:
        verdict = _verdict_from_config()
        lines.extend(["", "## GO / CONDITIONAL / NO-GO", ""])
        if verdict == "GO":
            lines.append(f"**{verdict}** — configs validate at report generation time.")
        else:
            lines.append(f"**NO-GO** — fix config validation errors before release.")
        lines.append("")
    return "\n".join(lines) + "\n"


def report_create(name: str, report_type: str) -> None:
    console = Console()
    rt = report_type.strip().lower()
    if rt not in REPORT_TYPES:
        console.print(f"[red]Unknown report type: {report_type}[/red]")
        raise typer.Exit(1)
    _ensure_project(name)
    db = get_memory_db_path()
    if not db.is_file():
        console.print("[red]Run memory init then memory sync-projects first[/red]")
        raise typer.Exit(1)
    sync_projects_from_registry(db)
    path = _report_path(name, rt)
    path.write_text(_body(name, rt), encoding="utf-8")
    add_analysis_report(db, name, rt, str(path.resolve()))
    write_audit(
        event="report_create",
        payload={"project": name, "type": rt, "path": str(path)},
        logs_root=get_logs_dir(),
    )
    console.print(f"[green]Wrote[/green] {path}")


def report_list(name: str) -> None:
    console = Console()
    db = get_memory_db_path()
    if not db.is_file():
        console.print("[yellow]No memory DB[/yellow]")
        return
    rows = list_analysis_reports(db, name)
    if not rows:
        console.print("(no reports)")
        return
    t = Table(title=f"Reports — {name}")
    t.add_column("Type")
    t.add_column("Path")
    t.add_column("Created (UTC)")
    for rtype, rpath, created in rows:
        t.add_row(rtype, rpath, str(created))
    console.print(t)


def report_latest(name: str) -> None:
    console = Console()
    db = get_memory_db_path()
    if not db.is_file():
        console.print("[yellow]No memory DB[/yellow]")
        return
    row = latest_analysis_report(db, name)
    if not row:
        console.print("(no reports)")
        return
    rtype, rpath, created = row
    console.print(f"Latest: {rtype}")
    console.print(f"Path: {rpath}")
    console.print(f"Created: {created}")
