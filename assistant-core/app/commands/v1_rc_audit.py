"""V1 release candidate audit (Sprint 22)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console

from app.commands.integrations import collect_integration_issues
from app.config.loader import ConfigError, load_and_validate_configs, load_project_registry
from app.memory.repository import list_analysis_reports
from app.paths import get_configs_dir, get_memory_db_path, get_workspace_dir


def run_v1_rc_audit() -> Path:
    """Run checklist and write markdown report under workspace/outputs/reports/V1/."""
    console = Console()
    lines: list[str] = [
        "# ATLAS V1 Release Candidate Audit",
        "",
        f"- Generated (UTC): {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Checklist",
        "",
    ]
    critical: list[str] = []
    warnings: list[str] = []

    def tick(ok: bool, label: str, detail: str = "") -> None:
        mark = "[x]" if ok else "[ ]"
        suf = f" — {detail}" if detail else ""
        lines.append(f"- {mark} {label}{suf}")

    reg = None
    try:
        load_and_validate_configs()
        tick(True, "Config validate (settings + registry + safety + MCP)")
        reg = load_project_registry()
    except ConfigError as exc:
        tick(False, "Config validate", str(exc))
        critical.append("config")

    gen_dir = get_configs_dir() / "generated"
    all_gen = all((gen_dir / n).is_file() for n in ("cursor.mcp.json", "vscode.mcp.json", "codex.config.toml"))
    tick(all_gen, "MCP generated configs present", "" if all_gen else str(gen_dir))
    if not all_gen:
        warnings.append("mcp-generate")

    db = get_memory_db_path()
    tick(db.is_file(), "SQLite memory DB", str(db))
    if not db.is_file():
        warnings.append("memory-db")

    if reg is not None:
        tick(True, "Project registry readable", f"{len(reg.projects)} project(s)")
        for p in reg.projects:
            has_agents = (p.root / "AGENTS.md").is_file() or (p.root / "assistant-core" / "AGENTS.md").is_file()
            if not has_agents:
                tick(True, f"Integrations ({p.name})", "skipped (no AGENTS.md; run instructions generate)")
                warnings.append(f"no-agents:{p.name}")
                continue
            issues = collect_integration_issues(p.name)
            ok = not issues
            tick(ok, f"Integrations ({p.name})", "; ".join(issues[:5]) if issues else "")
            if issues:
                critical.append(f"integrations:{p.name}")

    any_report = False
    if reg is not None and db.is_file():
        for p in reg.projects:
            if list_analysis_reports(db, p.name):
                any_report = True
                break
    has_projects = bool(reg and reg.projects)
    tick(not has_projects or any_report, "At least one analysis report in DB", "")
    if has_projects and not any_report:
        warnings.append("reports")

    lines.extend(["", "## Verdict", ""])
    if critical:
        verdict = "NO-GO"
        lines.append(f"**{verdict}** — fix: {', '.join(sorted(set(critical)))}")
    elif warnings:
        verdict = "CONDITIONAL"
        lines.append(f"**{verdict}** — address: {', '.join(sorted(set(warnings)))}")
    else:
        verdict = "GO"
        lines.append(f"**{verdict}** — V1 RC criteria satisfied at audit time.")

    lines.extend(
        [
            "",
            "## Risks",
            "",
            "- Static audit only; does not run build/test pipelines.",
            "- MCP security depends on generated configs and local policy discipline.",
            "",
        ]
    )

    out_dir = get_workspace_dir() / "outputs" / "reports" / "V1"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"v1-rc-audit-{ts}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    console.print(f"[green]Wrote[/green] {path}")
    console.print(f"Verdict: {verdict}")
    if verdict == "NO-GO":
        raise typer.Exit(1)
    return path
