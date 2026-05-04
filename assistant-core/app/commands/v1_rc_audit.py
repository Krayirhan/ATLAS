"""V1 release candidate audit (Sprint 22)."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import typer
from rich.console import Console

from app.commands.integrations import partition_integration_issues
from app.config.loader import ConfigError, load_and_validate_configs, load_project_registry
from app.memory.repository import list_analysis_reports
from app.paths import get_atlas_root, get_configs_dir, get_memory_db_path, get_workspace_dir


def _run_pytest_probe() -> tuple[bool, str]:
    ac = get_atlas_root() / "assistant-core"
    if not ac.is_dir():
        return False, "assistant-core missing"
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=str(ac),
        capture_output=True,
        text=True,
        timeout=300,
    )
    tail = (proc.stdout or "") + (proc.stderr or "")
    tail = tail.strip()[-800:] if tail else "(no output)"
    return proc.returncode == 0, tail


def _generated_mcp_leaks_d_atlas() -> bool:
    gen = get_configs_dir() / "generated" / "cursor.mcp.json"
    if not gen.is_file():
        return False
    try:
        blob = gen.read_text(encoding="utf-8-sig").lower()
    except OSError:
        return False
    norm = blob.replace("/", "\\")
    return r"d:\atlas" in norm


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
    optional_notes: list[str] = []

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

    if _generated_mcp_leaks_d_atlas():
        tick(False, "MCP generated cursor.mcp.json must not reference D:\\ATLAS", "")
        critical.append("mcp-d-atlas-leak")
    else:
        tick(True, "MCP generated configs do not advertise D:\\ATLAS as workspace", "")

    db = get_memory_db_path()
    tick(db.is_file(), "SQLite memory DB", str(db))
    if not db.is_file():
        warnings.append("memory-db")

    py_ok, py_tail = _run_pytest_probe()
    tick(py_ok, "pytest -q (assistant-core)", py_tail.replace("\n", " ")[:200])
    if not py_ok:
        critical.append("pytest")

    if reg is not None:
        tick(True, "Project registry readable", f"{len(reg.projects)} project(s)")
        for p in reg.projects:
            root_s = str(Path(p.root).resolve())
            if root_s.upper().startswith("D:\\ATLAS") or root_s.upper().startswith("D:/ATLAS"):
                tick(False, f"Project root must not be operational D:\\ATLAS ({p.name})", root_s)
                critical.append(f"d-atlas-root:{p.name}")
            if p.name.lower() == "benimformum":
                tick(True, f"Registry note ({p.name})", "BenimFormum is not the intended pilot; remove if unused.")
                warnings.append("benimformum-registry")
            has_agents = (p.root / "AGENTS.md").is_file() or (p.root / "assistant-core" / "AGENTS.md").is_file()
            if not has_agents:
                tick(True, f"Integrations critical ({p.name})", "skipped (no AGENTS.md; run instructions generate)")
                warnings.append(f"no-agents:{p.name}")
                continue
            crit, opt = partition_integration_issues(p.name)
            ok = not crit
            tick(ok, f"Integrations critical ({p.name})", "; ".join(crit[:5]) if crit else "")
            if crit:
                critical.append(f"integrations:{p.name}")
            for o in opt:
                optional_notes.append(f"{p.name}: {o}")

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

    lines.extend(["", "## Static notes", ""])
    lines.append("- `command preview` never executes shell commands (V1 design).")
    lines.append("- Full-disk MCP and autonomous coding agents are out of V1 scope.")

    if optional_notes:
        lines.extend(["", "## Optional integration gaps (non-blocking)", ""])
        for n in optional_notes[:20]:
            lines.append(f"- {n}")
        if len(optional_notes) > 20:
            lines.append(f"- … ({len(optional_notes) - 20} more)")

    lines.extend(["", "## Verdict", ""])
    if critical:
        verdict = "NO-GO"
        lines.append(f"**{verdict}** — critical: {', '.join(sorted(set(critical)))}")
    elif warnings:
        verdict = "CONDITIONAL"
        lines.append(f"**{verdict}** — warnings: {', '.join(sorted(set(warnings)))}")
    else:
        verdict = "GO"
        lines.append(f"**{verdict}** — V1 RC criteria satisfied at audit time.")

    lines.extend(
        [
            "",
            "## Risks",
            "",
            "- Static audit plus pytest; does not run MCP servers or terminal commands.",
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
