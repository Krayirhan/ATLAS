"""Typer entrypoint: `python -m app.cli` from assistant-core directory."""

from __future__ import annotations

from pathlib import Path

import typer

from app.commands.command import command_check, command_preview
from app.commands.ai import ai_approval_command, ai_ask, ai_ask_agent, ai_calendar, ai_chat, ai_demo, ai_device, ai_doctor, ai_docs_audit, ai_home_preview, ai_intent_preview, ai_main, ai_memory, ai_notification_preview, ai_panel, ai_pc_preview, ai_plan, ai_reminder, ai_review, ai_security_audit, ai_voice, ai_warmup
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


@ai.command("plan")
def _ai_plan(
    goal: str = typer.Option(..., "--goal"),
    project: str = typer.Option(..., "--project"),
    provider: str | None = typer.Option(None, "--provider"),
    max_sprints: int = typer.Option(1, "--max-sprints"),
    show_sources: bool = typer.Option(False, "--show-sources"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ai_plan(
        goal=goal,
        project=project,
        provider=provider,
        max_sprints=max_sprints,
        show_sources=show_sources,
        as_json=as_json,
    )


@ai.command("review")
def _ai_review(
    project: str = typer.Option(..., "--project"),
    scope: str = typer.Option(..., "--scope"),
    provider: str | None = typer.Option(None, "--provider"),
    files: list[str] = typer.Option([], "--file"),
    max_files: int = typer.Option(12, "--max-files"),
    max_chars_per_file: int = typer.Option(2000, "--max-chars-per-file"),
    show_sources: bool = typer.Option(False, "--show-sources"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ai_review(
        project=project,
        scope=scope,
        provider=provider,
        files=files,
        max_files=max_files,
        max_chars_per_file=max_chars_per_file,
        show_sources=show_sources,
        as_json=as_json,
    )


approval = typer.Typer(help="Preview-only approval workflow")
ai.add_typer(approval, name="approval")


@approval.command("command")
def _ai_approval_command(
    project: str = typer.Option(..., "--project"),
    cmd: str = typer.Option(..., "--cmd"),
    reason: str = typer.Option("", "--reason"),
    source_agent: str = typer.Option("", "--source-agent"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ai_approval_command(
        project=project,
        cmd=cmd,
        reason=reason,
        source_agent=source_agent,
        as_json=as_json,
    )


@ai.command("security-audit")
def _ai_security_audit(
    project: str = typer.Option(..., "--project"),
    scope: str = typer.Option(..., "--scope"),
    provider: str | None = typer.Option(None, "--provider"),
    show_sources: bool = typer.Option(False, "--show-sources"),
    as_json: bool = typer.Option(False, "--json"),
    max_files: int = typer.Option(16, "--max-files"),
    max_chars_per_file: int = typer.Option(2000, "--max-chars-per-file"),
) -> None:
    ai_security_audit(
        project=project,
        scope=scope,
        provider=provider,
        show_sources=show_sources,
        as_json=as_json,
        max_files=max_files,
        max_chars_per_file=max_chars_per_file,
    )


@ai.command("main")
def _ai_main(
    user_message: str = typer.Argument(...),
    project: str = typer.Option(..., "--project"),
    provider: str | None = typer.Option(None, "--provider"),
    mode: str = typer.Option("auto", "--mode"),
    show_sources: bool = typer.Option(False, "--show-sources"),
    show_routing: bool = typer.Option(False, "--show-routing"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ai_main(
        user_message=user_message,
        project=project,
        provider=provider,
        mode=mode,
        show_sources=show_sources,
        show_routing=show_routing,
        as_json=as_json,
    )


@ai.command("intent")
def _ai_intent(
    user_text: str = typer.Argument(...),
    project: str = typer.Option(..., "--project"),
    source: str = typer.Option("text", "--source"),
    show_preview: bool = typer.Option(False, "--show-preview"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ai_intent_preview(
        user_text=user_text,
        project=project,
        source=source,
        show_preview=show_preview,
        as_json=as_json,
    )


@ai.command("pc-preview")
def _ai_pc_preview(
    user_text: str = typer.Argument(...),
    project: str = typer.Option(..., "--project"),
    source: str = typer.Option("text", "--source"),
    show_plan: bool = typer.Option(False, "--show-plan"),
    as_json: bool = typer.Option(False, "--json"),
    dry_run: bool = typer.Option(True, "--dry-run"),
) -> None:
    ai_pc_preview(
        user_text=user_text,
        project=project,
        source=source,
        show_plan=show_plan,
        as_json=as_json,
        dry_run=dry_run,
    )


@ai.command("chat")
def _ai_chat(
    user_text: str = typer.Argument(..., help="User message for the assistant"),
    project: str = typer.Option(..., "--project"),
    source: str = typer.Option("text", "--source"),
    session_id: str | None = typer.Option(None, "--session-id"),
    as_json: bool = typer.Option(False, "--json"),
    show_state: bool = typer.Option(False, "--show-state"),
    reset_session: bool = typer.Option(False, "--reset-session"),
) -> None:
    ai_chat(
        user_text=user_text,
        project=project,
        source=source,
        session_id=session_id,
        as_json=as_json,
        show_state=show_state,
        reset_session=reset_session,
    )


@ai.command("memory-personal")
def _ai_memory_personal(
    text: str = typer.Argument(..., help="Text command for memory"),
    project: str = typer.Option(..., "--project"),
    json_output: bool = typer.Option(False, "--json"),
    show_all: bool = typer.Option(False, "--show-all"),
    clear: bool = typer.Option(False, "--clear"),
    memory_type: str | None = typer.Option(None, "--type"),
    session_id: str | None = typer.Option(None, "--session-id"),
) -> None:
    from app.commands.ai import ai_memory_personal
    ai_memory_personal(
        project=project,
        text=text,
        json_output=json_output,
        show_all=show_all,
        clear=clear,
        memory_type_str=memory_type,
        session_id=session_id
    )


@ai.command("routine")
def _ai_routine(
    text: str = typer.Argument(None, help="Routine command"),
    project: str = typer.Option(..., "--project"),
    json_output: bool = typer.Option(False, "--json"),
    list_routines: bool = typer.Option(False, "--list"),
    show_preview: bool = typer.Option(False, "--show-preview"),
    source: str = typer.Option("text", "--source"),
) -> None:
    from app.commands.ai import ai_routine
    ai_routine(
        project=project,
        text=text,
        json_output=json_output,
        list_routines=list_routines,
        show_preview=show_preview,
        source=source
    )


@ai.command("voice")
def _ai_voice(
    project: str = typer.Option(..., "--project"),
    mock_transcript: str | None = typer.Option(None, "--mock-transcript"),
    audio_path: str | None = typer.Option(None, "--audio-path"),
    language: str = typer.Option("tr", "--language"),
    session_id: str | None = typer.Option(None, "--session-id"),
    speak: bool = typer.Option(False, "--speak"),
    as_json: bool = typer.Option(False, "--json"),
    show_transcript: bool = typer.Option(False, "--show-transcript"),
    show_safety: bool = typer.Option(False, "--show-safety"),
) -> None:
    ai_voice(
        project=project,
        mock_transcript=mock_transcript,
        audio_path=audio_path,
        language=language,
        session_id=session_id,
        speak=speak,
        as_json=as_json,
        show_transcript=show_transcript,
        show_safety=show_safety,
    )


@ai.command("device")
def _ai_device(
    text: str = typer.Argument(None, help="Device command to preview"),
    project: str = typer.Option(..., "--project"),
    list_devices: bool = typer.Option(False, "--list"),
    list_rooms: bool = typer.Option(False, "--rooms"),
    as_json: bool = typer.Option(False, "--json"),
    show_plan: bool = typer.Option(False, "--show-plan"),
    source: str = typer.Option("text", "--source"),
) -> None:
    ai_device(
        project=project,
        text=text,
        list_devices=list_devices,
        list_rooms=list_rooms,
        as_json=as_json,
        show_plan=show_plan,
        source=source,
    )


@ai.command("home-preview")
def _ai_home_preview(
    text: str = typer.Argument(None, help="Home control command to preview"),
    project: str = typer.Option(..., "--project"),
    as_json: bool = typer.Option(False, "--json"),
    show_plan: bool = typer.Option(False, "--show-plan"),
    adapter_status: bool = typer.Option(False, "--adapter-status"),
    capabilities: bool = typer.Option(False, "--capabilities"),
    source: str = typer.Option("text", "--source"),
) -> None:
    ai_home_preview(
        project=project,
        text=text,
        as_json=as_json,
        show_plan=show_plan,
        adapter_status=adapter_status,
        capabilities=capabilities,
        source=source,
    )


@ai.command("panel")
def _ai_panel(
    project: str = typer.Option(..., "--project"),
    submit: str | None = typer.Option(None, "--submit"),
    list_items: bool = typer.Option(False, "--list"),
    show: str | None = typer.Option(None, "--show"),
    approve: str | None = typer.Option(None, "--approve"),
    deny: str | None = typer.Option(None, "--deny"),
    cancel: str | None = typer.Option(None, "--cancel"),
    clear: bool = typer.Option(False, "--clear"),
    as_json: bool = typer.Option(False, "--json"),
    status: str | None = typer.Option(None, "--status"),
    source: str = typer.Option("text", "--source"),
) -> None:
    ai_panel(
        project=project,
        submit=submit,
        list_items=list_items,
        show=show,
        approve=approve,
        deny=deny,
        cancel=cancel,
        clear=clear,
        as_json=as_json,
        status=status,
        source=source,
    )


@ai.command("reminder")
def _ai_reminder(
    text: str = typer.Argument(None, help="Reminder command"),
    project: str = typer.Option(..., "--project"),
    list_items: bool = typer.Option(False, "--list"),
    cancel: str | None = typer.Option(None, "--cancel"),
    as_json: bool = typer.Option(False, "--json"),
    source: str = typer.Option("text", "--source"),
) -> None:
    ai_reminder(
        project=project,
        text=text,
        list_items=list_items,
        cancel=cancel,
        as_json=as_json,
        source=source,
    )


@ai.command("calendar")
def _ai_calendar(
    text: str = typer.Argument(None, help="Calendar command"),
    project: str = typer.Option(..., "--project"),
    list_drafts: bool = typer.Option(False, "--list-drafts"),
    cancel_draft: str | None = typer.Option(None, "--cancel-draft"),
    as_json: bool = typer.Option(False, "--json"),
    source: str = typer.Option("text", "--source"),
) -> None:
    ai_calendar(
        project=project,
        text=text,
        list_drafts=list_drafts,
        cancel_draft=cancel_draft,
        as_json=as_json,
        source=source,
    )


@ai.command("notification-preview")
def _ai_notification_preview(
    project: str = typer.Option(..., "--project"),
    title: str = typer.Option(..., "--title"),
    body: str = typer.Option(..., "--body"),
    channel: str = typer.Option("cli", "--channel"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    ai_notification_preview(
        project=project,
        title=title,
        body=body,
        channel=channel,
        as_json=as_json,
    )


@ai.command("docs-audit")
def _ai_docs_audit(
    project: str = typer.Option(..., "--project"),
    scope: str = typer.Option(..., "--scope"),
    provider: str | None = typer.Option(None, "--provider"),
    show_sources: bool = typer.Option(False, "--show-sources"),
    as_json: bool = typer.Option(False, "--json"),
    max_files: int = typer.Option(16, "--max-files"),
    max_chars_per_file: int = typer.Option(2000, "--max-chars-per-file"),
) -> None:
    ai_docs_audit(
        project=project,
        scope=scope,
        provider=provider,
        show_sources=show_sources,
        as_json=as_json,
        max_files=max_files,
        max_chars_per_file=max_chars_per_file,
    )


@ai.command("demo")
def _ai_demo(
    project: str = typer.Option(..., "--project"),
    list_scenarios: bool = typer.Option(False, "--list", help="List all available demo scenarios"),
    scenario_id: str | None = typer.Option(None, "--scenario", help="Run a specific scenario by ID"),
    category: str | None = typer.Option(None, "--category", help="Run all scenarios in a category"),
    run_all: bool = typer.Option(False, "--all", help="Run all demo scenarios"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
    as_markdown: bool = typer.Option(False, "--markdown", help="Output as Markdown report"),
    output: str | None = typer.Option(None, "--output", help="Write report to file (workspace/outputs/demo/)"),
    show_safety: bool = typer.Option(False, "--show-safety", help="Show safety flag summary"),
    no_write: bool = typer.Option(False, "--no-write", help="Suppress file writing"),
) -> None:
    """Sprint 50 end-to-end personal assistant demo runner."""
    ai_demo(
        project=project,
        list_scenarios=list_scenarios,
        scenario_id=scenario_id,
        category=category,
        run_all=run_all,
        as_json=as_json,
        as_markdown=as_markdown,
        output=output,
        show_safety=show_safety,
        no_write=no_write,
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
