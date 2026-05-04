"""Report generator (Sprint 19)."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from app.commands.integrations import partition_integration_issues
from app.config.loader import ConfigError, load_and_validate_configs, load_project_registry, load_safety_policy
from app.logging.audit import write_audit
from app.memory.repository import (
    add_analysis_report,
    latest_analysis_report,
    list_analysis_reports,
    sync_projects_from_registry,
)
from app.paths import get_atlas_root, get_configs_dir, get_logs_dir, get_memory_db_path, get_workspace_dir


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


def _assistant_core_cwd() -> Path:
    return get_atlas_root() / "assistant-core"


def _cli_probe(args: list[str]) -> tuple[int, str]:
    if os.environ.get("ATLAS_REPORT_LIGHT") == "1":
        return 0, "(skipped: ATLAS_REPORT_LIGHT=1 avoids nested CLI during tests)"
    cwd = _assistant_core_cwd()
    if not cwd.is_dir():
        return 999, "assistant-core directory missing"
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "app.cli", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=180,
        )
        out = ((proc.stdout or "") + (proc.stderr or "")).strip()
        return proc.returncode, out[-1500:] if out else "(no output)"
    except Exception as exc:  # noqa: BLE001
        return 999, str(exc)[:800]


def _pytest_probe() -> tuple[int, str]:
    if os.environ.get("ATLAS_REPORT_LIGHT") == "1":
        return 0, "(skipped: ATLAS_REPORT_LIGHT=1 avoids nested pytest during tests)"
    cwd = _assistant_core_cwd()
    if not cwd.is_dir():
        return 999, "assistant-core directory missing"
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=300,
        )
        out = ((proc.stdout or "") + (proc.stderr or "")).strip()
        return proc.returncode, out[-1200:] if out else "(no output)"
    except Exception as exc:  # noqa: BLE001
        return 999, str(exc)[:800]


def _verdict_for_report(project_name: str) -> str:
    try:
        load_and_validate_configs()
    except ConfigError:
        return "NO-GO"
    crit, _opt = partition_integration_issues(project_name)
    if crit:
        return "CONDITIONAL"
    return "GO"


def _deep_report_sections(project_name: str, p, report_type: str) -> list[str]:
    """Shared markdown sections for depth report types (Sprint 27)."""
    kb = _kb_path(p, project_name)
    gen = get_configs_dir() / "generated"
    ws = get_workspace_dir()
    iso = datetime.now(timezone.utc).isoformat()
    lines: list[str] = [
        "## Report type",
        "",
        f"- `{report_type}`",
        "",
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
        "## Generated at",
        "",
        f"- `{iso}` (UTC)",
        "",
        "## Config status",
        "",
    ]
    try:
        load_and_validate_configs()
        lines.append("- **OK** — settings, registry, safety, and MCP master validate.")
    except ConfigError as exc:
        lines.append(f"- **FAIL** — {exc}")
    lines.extend(["", "## Registry status", ""])
    try:
        reg = load_project_registry()
        names = [x.name for x in reg.projects]
        lines.append(f"- Projects: {', '.join(names) if names else '(none)'}")
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
        if any(r"d:\atlas" in str(b or "").lower().replace("/", "\\") for b in pol.blocked_paths):
            lines.append("- `D:\\\\ATLAS` appears in blocked_paths (legacy path guard).")
    except ConfigError as exc:
        lines.append(f"- **FAIL** — {exc}")
    lines.extend(["", "## MCP status", ""])
    for fname in ("cursor.mcp.json", "vscode.mcp.json", "codex.config.toml"):
        fp = gen / fname
        lines.append(f"- `{fp.name}`: {'present' if fp.is_file() else 'missing'}")
    lines.append(f"- `workspace-filesystem` target (validated on `config validate`): `{ws.resolve()}`")
    lines.extend(["", "## Memory status", ""])
    db = get_memory_db_path()
    lines.append(f"- DB path: `{db}` — {'present' if db.is_file() else 'missing (run memory init)'}")
    lines.extend(["", "## Context manager status", ""])
    ctx = ws / "context"
    lines.append(f"- Context dir exists: **{ctx.is_dir()}** (`{ctx}`)")
    lines.append("- Planned read order is produced by `context build`; token budgets are **estimated**, not LLM-accurate.")
    lines.extend(["", "## Logs status", ""])
    logs = get_logs_dir()
    lines.append(f"- Logs root exists: **{logs.is_dir()}** (`{logs}`)")
    doc_code, doc_tail = _cli_probe(["doctor"])
    docf_code, docf_tail = _cli_probe(["doctor", "--full"])
    lines.extend(["", "## Doctor status", ""])
    lines.append(f"- `python -m app.cli doctor` exit code: **{doc_code}**")
    lines.append(f"- `python -m app.cli doctor --full` exit code: **{docf_code}**")
    if doc_code != 0 or docf_code != 0:
        lines.append("")
        lines.append("```text")
        lines.append(doc_tail[:800])
        lines.append("```")
    py_code, py_tail = _pytest_probe()
    lines.extend(["", "## Test status", ""])
    lines.append(f"- `python -m pytest -q` exit code: **{py_code}** (cwd: `{_assistant_core_cwd()}`)")
    if py_code != 0:
        lines.append("")
        lines.append("```text")
        lines.append(py_tail[:800])
        lines.append("```")
    lines.extend(["", "## Known warnings", ""])
    lines.append("- Optional tools (node, npm, git, docker) may warn under `doctor --full` on minimal machines.")
    crit_i, opt_i = partition_integration_issues(project_name)
    if opt_i:
        lines.append("- Optional integration gaps (Copilot/Codex/Cursor files) may exist without failing V1 RC.")
    lines.extend(["", "## Security risks", ""])
    lines.append("- MCP helpers are not full production MCP servers; no full-disk workspace; `command preview` does not execute.")
    lines.append("- `D:\\\\ATLAS` must not be used as an operational root; policy may block it explicitly.")
    lines.extend(["", "## Missing features (expected for V1)", ""])
    lines.append("- No LLM provider adapters, no `ai ask`, no autonomous coding agents, no RAG index, no desktop UI.")
    lines.extend(["", "## Next actions", ""])
    lines.append("- Run `audit v1-rc` after substantive config changes; keep `mcp generate --dry-run` in CI-style checks.")
    lines.append("- Sprint 28+: AI Layer Foundation (read-only design first).")
    return lines


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
        lines.extend(_deep_report_sections(project_name, p, report_type))

    if report_type == "integration-check":
        crit, opt = partition_integration_issues(project_name)
        lines.extend(["", "## Monorepo layout (ATLAS self-project)", ""])
        lines.append(f"- Monorepo root: `{get_atlas_root().resolve()}`")
        lines.append(f"- Python CLI package: `{_assistant_core_cwd().resolve()}`")
        lines.append("- Integration files may live under `assistant-core/` when `AGENTS.md` is only there (see `instruction_check_root`).")
        lines.extend(["", "## Integration check detail", ""])
        if crit:
            lines.append("**Critical issues:**")
            for i in crit:
                lines.append(f"- {i}")
        else:
            lines.append("**Critical issues:** none")
        lines.append("")
        if opt:
            lines.append("**Optional gaps (non-blocking):**")
            for i in opt:
                lines.append(f"- {i}")
        else:
            lines.append("**Optional gaps:** none")
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
        lines.append("- Run `python -m app.cli audit v1-rc` for the authoritative checklist under `workspace/outputs/reports/V1/`.")
        lines.append("- This report embeds live probes above; treat audit markdown as the formal RC record.")
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
        verdict = _verdict_for_report(project_name)
        lines.extend(["", "## GO / CONDITIONAL / NO-GO", ""])
        if verdict == "GO":
            lines.append(f"**{verdict}** — configs validate and no critical integration gaps for `{project_name}`.")
        elif verdict == "CONDITIONAL":
            lines.append(f"**{verdict}** — configs validate but integration critical issues remain; see Integration section.")
        else:
            lines.append(f"**{verdict}** — config validation failed; fix before release.")
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
