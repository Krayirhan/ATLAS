"""Typer entrypoint: `python -m app.cli` from assistant-core directory."""

from __future__ import annotations

from pathlib import Path

import typer

from app.commands.command import command_check, command_preview
from app.commands.ai import ai_ask, ai_ask_agent, ai_doctor, ai_memory, ai_warmup
from app.commands.config import validate_configs
from app.commands.context import context_build, context_show_plan
from app.commands.doctor import doctor
from app.commands.instructions import instructions_check, instructions_generate, instructions_preview
from app.commands.integrations import integrations_check
from app.commands.knowledge import knowledge_init
from app.commands.logs import logs_list, logs_project, logs_show
from app.commands.mcp import mcp_generate_cmd, mcp_install_cmd, mcp_list_cmd
from app.commands.memory import (
    memory_add_decision,
    memory_init,
    memory_list_decisions,
    memory_project_status,
    memory_sync_projects,
)
from app.commands.notebooklm import notebooklm_import, notebooklm_list, notebooklm_validate
from app.commands.onboard import onboard_project
from app.commands.paths import paths_cmd
from app.commands.project import project_add, project_list, project_show, project_validate
from app.commands.report import report_create, report_latest, report_list
from app.commands.safety import safety_show
from app.commands.v1_rc_audit import run_v1_rc_audit

app = typer.Typer(help="ATLAS AI assistant control plane (local-first).")

app.command()(doctor)
app.command("paths")(paths_cmd)

cfg = typer.Typer(help="Validate JSON configs")
app.add_typer(cfg, name="config")


@cfg.command("validate")
def _config_validate() -> None:
    validate_configs()


safety = typer.Typer(help="Safety policy")
app.add_typer(safety, name="safety")


@safety.command("show")
def _safety_show() -> None:
    safety_show()


mcp = typer.Typer(help="MCP config generation")
app.add_typer(mcp, name="mcp")


@mcp.command("list")
def _mcp_list() -> None:
    mcp_list_cmd()


@mcp.command("generate")
def _mcp_generate(
    target: str | None = typer.Option(
        None,
        "--target",
        help="cursor | vscode | codex | all (default: all)",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview output without writing files"),
) -> None:
    mcp_generate_cmd(target=target, dry_run=dry_run)


@mcp.command("install")
def _mcp_install(
    target: str = typer.Option(..., "--target"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    project: str | None = typer.Option(None, "--project"),
) -> None:
    mcp_install_cmd(target=target, dry_run=dry_run, project=project)


proj = typer.Typer(help="Project registry")
app.add_typer(proj, name="project")


@proj.command("add")
def _proj_add(
    name: str = typer.Option(..., "--name"),
    project_type: str = typer.Option(..., "--type"),
    root: Path = typer.Option(..., "--root", exists=True, file_okay=False, dir_okay=True),
    knowledge: Path | None = typer.Option(None, "--knowledge", exists=True, file_okay=False, dir_okay=True),
    build_command: str = typer.Option("", "--build-command"),
    test_command: str = typer.Option("", "--test-command"),
    lint_command: str = typer.Option("", "--lint-command"),
    forbid: list[str] = typer.Option([], "--forbid"),
) -> None:
    project_add(
        name=name,
        project_type=project_type,
        root=root,
        knowledge=knowledge,
        build_command=build_command,
        test_command=test_command,
        lint_command=lint_command,
        forbid=forbid,
    )


@proj.command("list")
def _proj_list() -> None:
    project_list()


@proj.command("show")
def _proj_show(name: str) -> None:
    project_show(name)


@proj.command("validate")
def _proj_validate(name: str) -> None:
    project_validate(name)


instr = typer.Typer(help="Instruction templates")
app.add_typer(instr, name="instructions")


@instr.command("preview")
def _instr_preview(name: str) -> None:
    instructions_preview(name)


@instr.command("generate")
def _instr_gen(name: str) -> None:
    instructions_generate(name)


@instr.command("check")
def _instr_check(name: str) -> None:
    instructions_check(name)


mem = typer.Typer(help="SQLite memory")
app.add_typer(mem, name="memory")


@mem.command("init")
def _mem_init() -> None:
    memory_init()


@mem.command("sync-projects")
def _mem_sync() -> None:
    memory_sync_projects()


@mem.command("project-status")
def _mem_status(
    name: str,
    new_status: str | None = typer.Option(None, "--set"),
) -> None:
    memory_project_status(name, new_status=new_status)


@mem.command("add-decision")
def _mem_add_decision(
    name: str,
    title: str = typer.Option(..., "--title"),
    body: str = typer.Option(..., "--body"),
) -> None:
    memory_add_decision(name, title=title, body=body)


@mem.command("list-decisions")
def _mem_list_decisions(name: str) -> None:
    memory_list_decisions(name)


nb = typer.Typer(help="NotebookLM imports")
app.add_typer(nb, name="notebooklm")


@nb.command("import")
def _nb_import(
    name: str = typer.Argument(...),
    source: Path = typer.Option(..., "--source", exists=True, file_okay=True, dir_okay=False),
) -> None:
    notebooklm_import(name, source=source)


@nb.command("list")
def _nb_list() -> None:
    notebooklm_list()


@nb.command("validate")
def _nb_validate(name: str) -> None:
    notebooklm_validate(name)


ctx = typer.Typer(help="Context manager")
app.add_typer(ctx, name="context")


@ctx.command("build")
def _ctx_build(
    project: str = typer.Argument(...),
    task: str = typer.Option(..., "--task"),
) -> None:
    context_build(project, task=task)


@ctx.command("show-plan")
def _ctx_show(
    project: str = typer.Argument(...),
    task: str = typer.Option(..., "--task"),
) -> None:
    context_show_plan(project, task=task)


cmd = typer.Typer(help="Command safety")
app.add_typer(cmd, name="command")


@cmd.command("check")
def _cmd_check(
    project: str = typer.Argument(...),
    cmd_str: str = typer.Option(..., "--cmd"),
) -> None:
    command_check(project, cmd=cmd_str)


@cmd.command("preview")
def _cmd_preview(
    project: str = typer.Argument(...),
    command_type: str = typer.Option(..., "--type"),
) -> None:
    command_preview(project, command_type=command_type)


logs = typer.Typer(help="Audit logs")
app.add_typer(logs, name="logs")


@logs.command("list")
def _logs_list() -> None:
    logs_list()


@logs.command("show")
def _logs_show(last: int = typer.Option(10, "--last")) -> None:
    logs_show(last=last)


@logs.command("project")
def _logs_project(
    name: str = typer.Argument(..., help="Project name to filter"),
    last: int = typer.Option(10, "--last", help="Max matching JSONL records to show"),
) -> None:
    logs_project(name, last=last)


integrations = typer.Typer(help="Tool integration checks")
app.add_typer(integrations, name="integrations")


@integrations.command("check")
def _integrations_check(name: str) -> None:
    integrations_check(name)


knowledge = typer.Typer(help="Knowledge-base utilities")
app.add_typer(knowledge, name="knowledge")


@knowledge.command("init")
def _knowledge_init(
    name: str,
    force: bool = typer.Option(False, "--force"),
) -> None:
    knowledge_init(name, force=force)


rep = typer.Typer(help="Reports")
app.add_typer(rep, name="report")


@rep.command("create")
def _report_create(
    name: str = typer.Argument(...),
    report_type: str = typer.Option(..., "--type"),
) -> None:
    report_create(name, report_type=report_type)


@rep.command("list")
def _report_list(name: str = typer.Argument(...)) -> None:
    report_list(name)


@rep.command("latest")
def _report_latest(name: str = typer.Argument(...)) -> None:
    report_latest(name)


audit = typer.Typer(help="Release audits (Sprint 22)")
app.add_typer(audit, name="audit")


@audit.command("v1-rc")
def _audit_v1_rc() -> None:
    run_v1_rc_audit()


ai = typer.Typer(help="Read-only AI layer")
app.add_typer(ai, name="ai")


@ai.command("doctor")
def _ai_doctor() -> None:
    ai_doctor()


@ai.command("ask")
def _ai_ask(
    question: str = typer.Argument(...),
    project: str = typer.Option(..., "--project"),
    provider: str | None = typer.Option(None, "--provider"),
    show_context: bool = typer.Option(False, "--show-context"),
) -> None:
    ai_ask(question=question, project=project, provider=provider, show_context=show_context)


@ai.command("warmup")
def _ai_warmup(
    provider: str | None = typer.Option("ollama", "--provider"),
) -> None:
    ai_warmup(provider=provider)


@ai.command("memory")
def _ai_memory(
    project: str = typer.Option(..., "--project"),
    show_sources: bool = typer.Option(False, "--show-sources"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ai_memory(project=project, show_sources=show_sources, as_json=as_json)


@ai.command("ask-agent")
def _ai_ask_agent(
    question: str = typer.Argument(...),
    project: str = typer.Option(..., "--project"),
    provider: str | None = typer.Option(None, "--provider"),
    show_sources: bool = typer.Option(False, "--show-sources"),
    show_context: bool = typer.Option(False, "--show-context"),
) -> None:
    ai_ask_agent(
        question=question,
        project=project,
        provider=provider,
        show_sources=show_sources,
        show_context=show_context,
    )


@app.command("onboard")
def _onboard(
    repo_root: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    name: str = typer.Option(..., "--name"),
    project_type: str = typer.Option(..., "--type"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    build_command: str = typer.Option("", "--build-command"),
    test_command: str = typer.Option("", "--test-command"),
    lint_command: str = typer.Option("", "--lint-command"),
) -> None:
    onboard_project(
        repo_root=repo_root,
        name=name,
        project_type=project_type,
        dry_run=dry_run,
        build_command=build_command,
        test_command=test_command,
        lint_command=lint_command,
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
