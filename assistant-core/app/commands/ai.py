"""CLI commands for the read-only AI layer."""

from __future__ import annotations

import json
import sys

import typer
from rich.console import Console
from rich.table import Table

from app.agents.code_reviewer_agent import CodeReviewerAgent
from app.agents.main_agent import MainAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.security_auditor_agent import SecurityAuditorAgent
from app.agents.tool_approval_agent import ToolApprovalAgent
from app.agents.models import CodeReviewRequest, MainAgentRequest, PlannerRequest, ProjectQARequest, SecurityAuditRequest
from app.approval.models import ProposedCommand
from app.agents.planner_agent import PlannerAgent
from app.agents.project_qa_agent import ProjectQAAgent
from app.ai.context_loader import AIContextError
from app.ai.models import AIRequest
from app.ai.providers.base import AIProviderError
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.service import AIService


def _safe_console_text(text: str) -> str:
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        text.encode(encoding)
        return text
    except UnicodeEncodeError:
        return text.encode(encoding, errors="replace").decode(encoding, errors="replace")


def ai_doctor() -> None:
    console = Console()
    service = AIService()
    mock_health = MockAIProvider().health_check()
    ollama_health = service.provider_health("ollama")

    table = Table(title="ATLAS AI doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_row("default provider", service.default_provider_name())
    table.add_row("ollama base_url", service.ollama_base_url())
    table.add_row("ollama reachable", "ok" if "reachable" in ollama_health.message and ollama_health.ok else f"warn: {ollama_health.message}")
    table.add_row("ollama model", ollama_health.model if ollama_health.ok else f"warn: {ollama_health.message}")
    table.add_row("mock provider", "ok" if mock_health.ok else f"fail: {mock_health.message}")
    console.print(table)


def ai_ask(
    question: str = typer.Argument(..., help="Question to ask the read-only ATLAS AI layer"),
    project: str = typer.Option(..., "--project", help="Registered project name"),
    provider: str | None = typer.Option(None, "--provider", help="Override provider: mock | ollama"),
    show_context: bool = typer.Option(False, "--show-context", help="Print loaded context source list"),
) -> None:
    console = Console()
    service = AIService()
    try:
        response = service.ask(AIRequest(project=project, question=question, provider=provider, show_context=show_context))
    except (AIContextError, AIProviderError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    if show_context:
        console.print("[bold]Context sources[/bold]")
        for source in response.context_sources:
            console.print(
                f"- {source.kind}: {source.label} -> {source.path} "
                f"({source.metadata.get('char_count', len(source.content))} chars)"
            )
        console.print(
            f"Total context chars: {response.metadata.get('context_total_chars', 0)} / "
            f"{response.metadata.get('context_limit_chars', 0)}"
        )
        console.print("")
    console.print(response.text)


def ai_warmup(
    provider: str | None = typer.Option("ollama", "--provider", help="Warmup target provider"),
) -> None:
    console = Console()
    service = AIService()
    try:
        response = service.warmup(provider)
    except (AIContextError, AIProviderError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    table = Table(title="ATLAS AI warmup")
    table.add_column("Check")
    table.add_column("Status")
    table.add_row("provider", response.provider)
    table.add_row("model", response.model)
    table.add_row("keep_alive", str(response.metadata.get("keep_alive", "")))
    table.add_row("total_duration", str(response.metadata.get("total_duration", "")))
    table.add_row("load_duration", str(response.metadata.get("load_duration", "")))
    table.add_row("result", "model loaded / warmed")
    console.print(table)


def ai_memory(
    project: str = typer.Option(..., "--project", help="Registered project name"),
    show_sources: bool = typer.Option(False, "--show-sources", help="Print source metadata"),
    as_json: bool = typer.Option(False, "--json", help="Render snapshot as JSON"),
) -> None:
    console = Console()
    agent = MemoryAgent()
    try:
        snapshot = agent.snapshot(project)
    except AIContextError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    if as_json:
        typer.echo(
            json.dumps(
                {
                    "project_name": snapshot.project_name,
                    "project_type": snapshot.project_type,
                    "root": snapshot.root,
                    "knowledge_path": snapshot.knowledge_path,
                    "release_status": snapshot.release_status[:400],
                    "warnings": snapshot.warnings,
                    "recent_reports": snapshot.recent_reports,
                    "sources": [
                        {
                            "type": source.source_type,
                            "label": source.label,
                            "path": source.path,
                            "char_count": source.char_count,
                        }
                        for source in snapshot.context_sources
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    console.print(f"[bold]Project[/bold]: {snapshot.project_name}")
    console.print(f"[bold]Type[/bold]: {snapshot.project_type}")
    console.print(f"[bold]Root[/bold]: {snapshot.root}")
    console.print(f"[bold]Knowledge[/bold]: {snapshot.knowledge_path}")
    console.print(f"[bold]Recent reports[/bold]: {len(snapshot.recent_reports)}")
    if snapshot.warnings:
        console.print("[bold]Warnings[/bold]")
        for warning in snapshot.warnings:
            console.print(f"- {warning}")
    if show_sources:
        console.print("[bold]Sources[/bold]")
        for source in snapshot.context_sources:
            console.print(f"- {source.source_type}: {source.label} -> {source.path} ({source.char_count} chars)")


def ai_ask_agent(
    question: str = typer.Argument(..., help="Question to ask the ProjectQAAgent"),
    project: str = typer.Option(..., "--project", help="Registered project name"),
    provider: str | None = typer.Option(None, "--provider", help="Override provider: mock | ollama"),
    show_sources: bool = typer.Option(False, "--show-sources", help="Print source metadata"),
    show_context: bool = typer.Option(False, "--show-context", help="Show source metadata and context limits"),
) -> None:
    console = Console()
    agent = ProjectQAAgent()
    try:
        result = agent.answer(
            request=ProjectQARequest(
                project_name=project,
                question=question,
                provider=provider,
                show_sources=show_sources,
                show_context=show_context,
            )
        )
    except (AIContextError, AIProviderError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    if show_sources or show_context:
        console.print("[bold]Sources[/bold]")
        for source in result.sources:
            console.print(f"- {source.source_type}: {source.label} -> {source.path} ({source.char_count} chars)")
    if show_context:
        console.print(
            f"Total context chars: {result.metadata.get('context_total_chars', 0)} / "
            f"{result.metadata.get('context_limit_chars', 0)}"
        )
        console.print("Prompt body hidden by design.")
    if result.warnings:
        console.print("[bold]Warnings[/bold]")
        for warning in result.warnings:
            console.print(f"- {warning}")
    console.print(_safe_console_text(result.answer))


def ai_plan(
    goal: str = typer.Option(..., "--goal", help="Planning goal"),
    project: str = typer.Option(..., "--project", help="Registered project name"),
    provider: str | None = typer.Option(None, "--provider", help="Override provider: mock | ollama"),
    max_sprints: int = typer.Option(1, "--max-sprints"),
    show_sources: bool = typer.Option(False, "--show-sources"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    console = Console()
    agent = PlannerAgent()
    try:
        result = agent.plan(
            PlannerRequest(
                project_name=project,
                goal=goal,
                provider=provider,
                max_sprints=max_sprints,
                show_sources=show_sources,
                as_json=as_json,
            )
        )
    except (AIContextError, AIProviderError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    if as_json:
        typer.echo(
            json.dumps(
                {
                    "agent_name": result.agent_name,
                    "project_name": result.project_name,
                    "goal": result.goal,
                    "status": result.status,
                    "plan_summary": result.plan_summary,
                    "warnings": result.warnings,
                    "sources": [
                        {
                            "type": source.source_type,
                            "label": source.label,
                            "path": source.path,
                            "char_count": source.char_count,
                        }
                        for source in result.sources
                    ],
                    "proposed_sprints": [
                        {
                            "sprint_name": sprint.sprint_name,
                            "objective": sprint.objective,
                            "scope": sprint.scope,
                            "out_of_scope": sprint.out_of_scope,
                            "expected_files": [{"path": item.path, "reason": item.reason} for item in sprint.expected_files],
                            "risks": [{"title": item.title, "detail": item.detail} for item in sprint.risks],
                            "acceptance_criteria": [item.text for item in sprint.acceptance_criteria],
                            "test_plan": [item.text for item in sprint.test_plan],
                            "validation_commands": sprint.validation_commands,
                            "next_dependency": sprint.next_dependency,
                        }
                        for sprint in result.proposed_sprints
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if show_sources:
        console.print("[bold]Sources[/bold]")
        for source in result.sources:
            console.print(f"- {source.source_type}: {source.label} -> {source.path} ({source.char_count} chars)")
    if result.warnings:
        console.print("[bold]Warnings[/bold]")
        for warning in result.warnings:
            console.print(f"- {warning}")
    console.print(result.plan_summary)


def ai_review(
    project: str = typer.Option(..., "--project", help="Registered project name"),
    scope: str = typer.Option(..., "--scope", help="Review scope"),
    provider: str | None = typer.Option(None, "--provider", help="Override provider: mock | ollama"),
    files: list[str] = typer.Option([], "--file", help="Optional extra file path(s) under ATLAS root"),
    max_files: int = typer.Option(12, "--max-files"),
    max_chars_per_file: int = typer.Option(2000, "--max-chars-per-file"),
    show_sources: bool = typer.Option(False, "--show-sources"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    console = Console()
    agent = CodeReviewerAgent()
    try:
        result = agent.review(
            CodeReviewRequest(
                project_name=project,
                scope=scope,
                provider=provider,
                files=files,
                max_files=max_files,
                max_chars_per_file=max_chars_per_file,
                show_sources=show_sources,
                as_json=as_json,
            )
        )
    except (AIContextError, AIProviderError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    if as_json:
        typer.echo(
            json.dumps(
                {
                    "agent_name": result.agent_name,
                    "project_name": result.project_name,
                    "scope": result.scope,
                    "status": result.status,
                    "summary": result.summary,
                    "warnings": result.warnings,
                    "metadata": result.metadata,
                    "findings": [
                        {
                            "severity": item.severity,
                            "category": item.category,
                            "title": item.title,
                            "description": item.description,
                            "affected_file": item.affected_file,
                            "evidence": item.evidence,
                            "recommendation": item.recommendation,
                            "test_suggestion": item.test_suggestion,
                        }
                        for item in result.findings
                    ],
                    "recommendations": [{"title": item.title, "text": item.text} for item in result.recommendations],
                    "test_suggestions": [item.text for item in result.test_suggestions],
                    "sources": [
                        {
                            "type": source.source_type,
                            "label": source.label,
                            "path": source.path,
                            "char_count": source.char_count,
                        }
                        for source in result.sources
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if show_sources:
        console.print("[bold]Sources[/bold]")
        for source in result.sources:
            console.print(f"- {source.source_type}: {source.label} -> {source.path} ({source.char_count} chars)")
    if result.warnings:
        console.print("[bold]Warnings[/bold]")
        for warning in result.warnings:
            console.print(f"- {warning}")
    console.print(result.summary)


def ai_approval_command(
    project: str = typer.Option(..., "--project", help="Registered project name"),
    cmd: str = typer.Option(..., "--cmd", help="Command string to evaluate"),
    reason: str = typer.Option("", "--reason", help="Why the action was proposed"),
    source_agent: str = typer.Option("", "--source-agent", help="Agent or component proposing the action"),
    as_json: bool = typer.Option(False, "--json", help="Render decision as JSON"),
) -> None:
    console = Console()
    agent = ToolApprovalAgent()
    decision = agent.evaluate_command(
        ProposedCommand(
            project_name=project,
            command=cmd,
            reason=reason,
            source_agent=source_agent,
        )
    )
    if as_json:
        typer.echo(
            json.dumps(
                {
                    "status": decision.status,
                    "risk_level": decision.risk_level,
                    "reason": decision.reason,
                    "approval_required": decision.approval_required,
                    "blocked": decision.blocked,
                    "safe_preview": decision.safe_preview,
                    "suggested_next_step": decision.suggested_next_step,
                    "audit_metadata": decision.audit_metadata,
                    "findings": [
                        {"severity": item.severity, "category": item.category, "detail": item.detail}
                        for item in decision.findings
                    ],
                    "requirements": [
                        {"requirement_type": item.requirement_type, "detail": item.detail}
                        for item in decision.requirements
                    ],
                    "preview": {
                        "summary": decision.preview.summary,
                        "command_preview": decision.preview.command_preview,
                        "working_directory": decision.preview.working_directory,
                    }
                    if decision.preview
                    else None,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    console.print(f"[bold]Status[/bold]: {decision.status}")
    console.print(f"[bold]Risk[/bold]: {decision.risk_level}")
    console.print(f"[bold]Reason[/bold]: {decision.reason}")
    console.print("[bold]Preview only[/bold]: command is not executed.")
    if decision.findings:
        console.print("[bold]Findings[/bold]")
        for item in decision.findings:
            console.print(f"- [{item.severity}] {item.category}: {item.detail}")
    if decision.requirements:
        console.print("[bold]Requirements[/bold]")
        for item in decision.requirements:
            console.print(f"- {item.requirement_type}: {item.detail}")
    if decision.preview:
        console.print("[bold]Preview[/bold]")
        console.print(f"- {decision.preview.summary}")
        if decision.preview.command_preview:
            console.print(f"- command: {decision.preview.command_preview}")
        if decision.preview.working_directory:
            console.print(f"- working_directory: {decision.preview.working_directory}")
    console.print(f"[bold]Next step[/bold]: {decision.suggested_next_step}")


def ai_security_audit(
    project: str = typer.Option(..., "--project", help="Registered project name"),
    scope: str = typer.Option(..., "--scope", help="Security audit scope"),
    provider: str | None = typer.Option(None, "--provider", help="Override provider: mock | ollama"),
    show_sources: bool = typer.Option(False, "--show-sources"),
    as_json: bool = typer.Option(False, "--json"),
    max_files: int = typer.Option(16, "--max-files"),
    max_chars_per_file: int = typer.Option(2000, "--max-chars-per-file"),
) -> None:
    console = Console()
    agent = SecurityAuditorAgent()
    try:
        result = agent.audit(
            SecurityAuditRequest(
                project_name=project,
                scope=scope,
                provider=provider,
                show_sources=show_sources,
                as_json=as_json,
                max_files=max_files,
                max_chars_per_file=max_chars_per_file,
            )
        )
    except (AIContextError, AIProviderError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    if as_json:
        typer.echo(
            json.dumps(
                {
                    "agent_name": result.agent_name,
                    "project_name": result.project_name,
                    "scope": result.scope,
                    "status": result.status,
                    "decision": result.decision,
                    "summary": result.summary,
                    "warnings": result.warnings,
                    "metadata": result.metadata,
                    "findings": [
                        {
                            "severity": item.severity,
                            "category": item.category,
                            "title": item.title,
                            "description": item.description,
                            "affected_file": item.affected_file,
                            "evidence": item.evidence,
                            "recommendation": item.recommendation,
                            "test_suggestion": item.test_suggestion,
                        }
                        for item in result.findings
                    ],
                    "controls": [{"name": item.name, "status": item.status, "detail": item.detail} for item in result.controls],
                    "agent_capabilities": [
                        {
                            "agent_name": item.agent_name,
                            "read_only": item.read_only,
                            "can_write_files": item.can_write_files,
                            "can_run_commands": item.can_run_commands,
                            "can_call_tools": item.can_call_tools,
                            "status": item.status,
                            "detail": item.detail,
                        }
                        for item in result.agent_capabilities
                    ],
                    "mcp_exposure": [{"target": item.target, "status": item.status, "detail": item.detail} for item in result.mcp_exposure],
                    "secret_exposure": [{"target": item.target, "status": item.status, "detail": item.detail} for item in result.secret_exposure],
                    "approval_policy": [{"check_name": item.check_name, "status": item.status, "detail": item.detail} for item in result.approval_policy],
                    "recommendations": result.recommendations,
                    "test_suggestions": result.test_suggestions,
                    "sources": [
                        {
                            "type": source.source_type,
                            "label": source.label,
                            "path": source.path,
                            "char_count": source.char_count,
                        }
                        for source in result.sources
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    console.print(f"[bold]Decision[/bold]: {result.decision}")
    console.print(f"[bold]Scope[/bold]: {result.scope}")
    if show_sources:
        console.print("[bold]Sources[/bold]")
        for source in result.sources:
            console.print(f"- {source.source_type}: {source.label} -> {source.path} ({source.char_count} chars)")
    if result.warnings:
        console.print("[bold]Warnings[/bold]")
        for warning in result.warnings:
            console.print(f"- {warning}")
    console.print(_safe_console_text(result.summary))


def ai_main(
    user_message: str = typer.Argument(..., help="User request for MainAgent"),
    project: str = typer.Option(..., "--project", help="Registered project name"),
    provider: str | None = typer.Option(None, "--provider", help="Override provider: mock | ollama"),
    mode: str = typer.Option("auto", "--mode", help="answer|plan|review|approval|security|auto"),
    show_sources: bool = typer.Option(False, "--show-sources"),
    show_routing: bool = typer.Option(False, "--show-routing"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    console = Console()
    agent = MainAgent()
    try:
        result = agent.handle(
            MainAgentRequest(
                project_name=project,
                user_message=user_message,
                provider=provider,
                preferred_mode=mode,
                show_sources=show_sources,
                show_routing=show_routing,
            )
        )
    except (AIContextError, AIProviderError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    if as_json:
        typer.echo(
            json.dumps(
                {
                    "agent_name": result.agent_name,
                    "project_name": result.project_name,
                    "task_type": result.task_type,
                    "response_mode": result.response_mode,
                    "route": result.metadata.get("route", {}),
                    "answer": result.answer,
                    "summary": result.summary,
                    "warnings": result.warnings,
                    "metadata": result.metadata,
                    "sources": [
                        {
                            "type": source.source_type,
                            "label": source.label,
                            "path": source.path,
                            "char_count": source.char_count,
                        }
                        for source in result.sources
                    ],
                    "safety": {
                        "read_only": result.safety.read_only if result.safety else True,
                        "can_write_files": result.safety.can_write_files if result.safety else False,
                        "can_run_commands": result.safety.can_run_commands if result.safety else False,
                        "can_call_tools": result.safety.can_call_tools if result.safety else False,
                        "approval_token_production": result.safety.approval_token_production if result.safety else False,
                    },
                    "sub_results": result.sub_results,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if show_routing:
        route = result.route
        console.print("[bold]Routing[/bold]")
        console.print(f"- task_type: {route.task_type}")
        console.print(f"- selected_agents: {', '.join(route.selected_agents)}")
        console.print(f"- reason: {route.reason}")
        console.print(f"- confidence: {route.confidence}")
        console.print(f"- requires_approval_check: {route.requires_approval_check}")
    if show_sources:
        console.print("[bold]Sources[/bold]")
        for source in result.sources:
            console.print(f"- {source.source_type}: {source.label} -> {source.path} ({source.char_count} chars)")
    if result.warnings:
        console.print("[bold]Warnings[/bold]")
        for warning in result.warnings:
            console.print(f"- {warning}")
    console.print(_safe_console_text(result.answer))
