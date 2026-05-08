"""CLI commands for the read-only AI layer."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from enum import Enum

import typer
from rich.console import Console
from rich.table import Table

from app.actions.intent_router import IntentRouter
from app.actions.models import IntentPreviewResult
from app.actions.types import ActionSource
from app.agents.code_reviewer_agent import CodeReviewerAgent
from app.agents.documentation_agent import DocumentationAgent
from app.agents.main_agent import MainAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.security_auditor_agent import SecurityAuditorAgent
from app.agents.tool_approval_agent import ToolApprovalAgent
from app.agents.models import (
    CodeReviewRequest,
    DocumentationAuditRequest,
    MainAgentRequest,
    PlannerRequest,
    ProjectQARequest,
    SecurityAuditRequest,
)
from app.approval.models import ProposedCommand
from app.agents.planner_agent import PlannerAgent
from app.agents.project_qa_agent import ProjectQAAgent
from app.ai.context_loader import AIContextError
from app.ai.models import AIRequest
from app.ai.providers.base import AIProviderError
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.service import AIService
from app.devices.planner import DeviceActionPlanner
from app.devices.registry import DeviceRegistry


def _safe_console_text(text: str) -> str:
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        text.encode(encoding)
        return text
    except UnicodeEncodeError:
        return text.encode(encoding, errors="replace").decode(encoding, errors="replace")


def _json_safe(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


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


def ai_docs_audit(
    project: str = typer.Option(..., "--project", help="Registered project name"),
    scope: str = typer.Option(..., "--scope", help="Documentation audit scope: readme|knowledge-base|notebooklm|roadmap|agents|release|all-light"),
    provider: str | None = typer.Option(None, "--provider", help="Override provider: mock | ollama"),
    show_sources: bool = typer.Option(False, "--show-sources"),
    as_json: bool = typer.Option(False, "--json"),
    max_files: int = typer.Option(16, "--max-files"),
    max_chars_per_file: int = typer.Option(2000, "--max-chars-per-file"),
) -> None:
    console = Console()
    agent = DocumentationAgent()
    try:
        result = agent.audit(
            DocumentationAuditRequest(
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
                        }
                        for item in result.findings
                    ],
                    "source_checks": [
                        {"label": item.label, "path": item.path, "status": item.status, "detail": item.detail}
                        for item in result.source_checks
                    ],
                    "roadmap_checks": [
                        {"check_name": item.check_name, "status": item.status, "detail": item.detail}
                        for item in result.roadmap_checks
                    ],
                    "consistency_checks": [
                        {"check_name": item.check_name, "status": item.status, "detail": item.detail}
                        for item in result.consistency_checks
                    ],
                    "recommendations": [
                        {"title": item.title, "text": item.text}
                        for item in result.recommendations
                    ],
                    "missing_docs": result.missing_docs,
                    "outdated_docs": result.outdated_docs,
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


def ai_intent_preview(
    user_text: str = typer.Argument(..., help="User text to route into intent/action preview"),
    project: str = typer.Option(..., "--project", help="Registered project name"),
    source: str = typer.Option("text", "--source", help="text|voice|routine|schedule|manual"),
    show_preview: bool = typer.Option(False, "--show-preview", help="Show preview and permission decision"),
    as_json: bool = typer.Option(False, "--json", help="Render router output as JSON"),
) -> None:
    console = Console()
    source_enum = _parse_action_source(source)
    result = IntentRouter().preview(user_text, source=source_enum)

    if as_json:
        payload = _intent_preview_payload(project, result)
        typer.echo(json.dumps(_json_safe(payload), ensure_ascii=False, indent=2))
        return

    console.print(f"[bold]Project[/bold]: {project}")
    console.print(f"[bold]Source[/bold]: {source_enum.value}")
    console.print(f"[bold]Intent[/bold]: {result.intent.category.value}")
    console.print(f"[bold]Confidence[/bold]: {result.intent.confidence}")
    if result.intent.target:
        console.print(f"[bold]Target[/bold]: {result.intent.target}")
    if result.intent.requires_clarification:
        console.print(f"[bold]Clarification[/bold]: {result.intent.ambiguity_reason or 'Clarification required'}")
    if result.action_candidate is not None:
        console.print(f"[bold]Action[/bold]: {result.action_candidate.action_type.value}")
        console.print(f"[bold]Risk[/bold]: {result.action_candidate.risk_level.value}")
    else:
        console.print("[bold]Action[/bold]: none")

    if show_preview:
        if result.permission_decision is not None:
            console.print(f"[bold]Permission[/bold]: {result.permission_decision.status.value}")
            console.print(f"[bold]Reason[/bold]: {result.permission_decision.reason}")
            if result.permission_decision.confirmation_prompt:
                console.print(f"[bold]Prompt[/bold]: {_safe_console_text(result.permission_decision.confirmation_prompt)}")
        elif result.clarification is not None:
            console.print(f"[bold]Permission[/bold]: clarification_required")
            console.print(f"[bold]Reason[/bold]: {_safe_console_text(result.clarification.reason)}")
        else:
            console.print("[bold]Permission[/bold]: no_action_required")
        if result.action_preview is not None:
            console.print(f"[bold]Preview[/bold]: {result.action_preview.summary}")
    if result.warnings:
        console.print("[bold]Warnings[/bold]")
        for warning in result.warnings:
            console.print(f"- {_safe_console_text(warning)}")
    console.print("[bold]Execution[/bold]: none")


def _parse_action_source(source: str) -> ActionSource:
    normalized = source.strip().lower()
    mapping = {
        "text": ActionSource.TEXT,
        "voice": ActionSource.VOICE,
        "routine": ActionSource.ROUTINE,
        "schedule": ActionSource.SCHEDULE,
        "manual": ActionSource.MANUAL,
    }
    if normalized not in mapping:
        raise typer.BadParameter("source must be one of: text, voice, routine, schedule, manual")
    return mapping[normalized]


def _parse_personal_source(source: str):
    from app.personal_assistant.models import ReminderSource

    return ReminderSource(_parse_action_source(source).value)


def _intent_preview_payload(project: str, result: IntentPreviewResult) -> dict[str, object]:
    return {
        "project": project,
        "raw_text": result.raw_text,
        "intent": asdict(result.intent),
        "action_candidate": asdict(result.action_candidate) if result.action_candidate is not None else None,
        "action_preview": asdict(result.action_preview) if result.action_preview is not None else None,
        "permission_decision": asdict(result.permission_decision) if result.permission_decision is not None else None,
        "clarification": asdict(result.clarification) if result.clarification is not None else None,
        "warnings": result.warnings,
        "metadata": result.metadata,
    }


def ai_pc_preview(
    user_text: str = typer.Argument(..., help="User text to route into PC action preview"),
    project: str = typer.Option(..., "--project", help="Registered project name"),
    source: str = typer.Option("text", "--source", help="text|voice|routine|schedule|manual"),
    show_plan: bool = typer.Option(False, "--show-plan", help="Show the generated PC control plan"),
    as_json: bool = typer.Option(False, "--json", help="Render output as JSON"),
    dry_run: bool = typer.Option(True, "--dry-run", help="Generate a dry-run plan"),
) -> None:
    from app.control.pc_adapter import PCControlAdapter
    
    console = Console()
    source_enum = _parse_action_source(source)
    router_result = IntentRouter().preview(user_text, source=source_enum)
    
    adapter = PCControlAdapter()
    
    if as_json:
        payload = _intent_preview_payload(project, router_result)
        if router_result.action_candidate and router_result.permission_decision:
            plan = adapter.build_plan(router_result.action_candidate, router_result.permission_decision, dry_run=dry_run)
            payload["pc_plan"] = asdict(plan)
            result = adapter.execute(plan)
            payload["pc_result"] = asdict(result)
        typer.echo(json.dumps(_json_safe(payload), ensure_ascii=False, indent=2))
        return

    if not router_result.action_candidate or not router_result.permission_decision:
        if router_result.clarification:
            console.print(f"Clarification required: {router_result.clarification.reason}")
        else:
            console.print("Blocked: No valid action candidate or permission decision.")
        return
        
    plan = adapter.build_plan(router_result.action_candidate, router_result.permission_decision, dry_run=dry_run)
    result = adapter.execute(plan)
    
    if show_plan:
        console.print(f"[bold]Plan[/bold]: {plan.summary}")
        console.print(f"[bold]Executable[/bold]: {plan.executable}")
        console.print(f"[bold]Execution Allowed[/bold]: {plan.execution_allowed}")
        if plan.blocked_reason:
            console.print(f"[bold]Blocked Reason[/bold]: {plan.blocked_reason}")
            
    console.print(f"[bold]Result Status[/bold]: {result.status.value}")
    console.print(f"[bold]Result Message[/bold]: {result.message}")
    if result.data:
        console.print(f"[bold]Data[/bold]: {json.dumps(result.data, indent=2, ensure_ascii=False)}")


def ai_device(
    project: str,
    text: str | None = None,
    list_devices: bool = False,
    list_rooms: bool = False,
    as_json: bool = False,
    show_plan: bool = False,
    source: str = "text",
) -> None:
    console = Console()
    registry = DeviceRegistry()
    planner = DeviceActionPlanner(registry=registry)

    if list_rooms:
        rooms = registry.list_rooms()
        if as_json:
            typer.echo(json.dumps(_json_safe([asdict(room) for room in rooms]), ensure_ascii=False, indent=2))
            return
        for room in rooms:
            console.print(f"- {room.display_name}")
        return

    if list_devices:
        devices = registry.list_devices()
        if as_json:
            typer.echo(json.dumps(_json_safe([asdict(device) for device in devices]), ensure_ascii=False, indent=2))
            return
        for device in devices:
            room = registry.get_room(device.room_id)
            console.print(f"- {device.display_name} ({device.device_type.value}, room: {room.display_name if room else device.room_id})")
        return

    if not text:
        console.print("[red]Device preview icin bir metin belirtmelisin.[/red]")
        raise typer.Exit(1)

    source_enum = _parse_action_source(source)
    result = planner.preview_device_action(text, source=source_enum)
    payload = {
        "project": project,
        "text": text,
        "status": result.status.value,
        "message": result.message,
        "device": asdict(result.device) if result.device is not None else None,
        "room": asdict(result.room) if result.room is not None else None,
        "resolution": asdict(result.resolution) if result.resolution is not None else None,
        "plan": asdict(result.plan) if result.plan is not None else None,
        "warnings": result.warnings,
        "metadata": result.metadata,
    }
    if as_json:
        typer.echo(json.dumps(_json_safe(payload), ensure_ascii=False, indent=2))
        return

    console.print(f"[bold]Project[/bold]: {project}")
    console.print(f"[bold]Status[/bold]: {result.status.value}")
    console.print(f"[bold]Message[/bold]: {_safe_console_text(result.message)}")
    if result.device is not None:
        console.print(f"[bold]Device[/bold]: {result.device.display_name}")
    if result.room is not None:
        console.print(f"[bold]Room[/bold]: {result.room.display_name}")
    if result.resolution is not None and result.resolution.requires_clarification:
        console.print(f"[bold]Clarification[/bold]: {_safe_console_text(result.resolution.ambiguity_reason)}")
        if result.resolution.candidates:
            console.print("[bold]Candidates[/bold]")
            for device in result.resolution.candidates:
                console.print(f"- {device.display_name}")
    if show_plan and result.plan is not None:
        console.print(f"[bold]Plan[/bold]: {_safe_console_text(result.plan.summary)}")
        console.print(f"[bold]Capability[/bold]: {result.plan.capability}")
        console.print(f"[bold]Risk[/bold]: {result.plan.risk_level.value}")
        console.print(f"[bold]Confirmation Required[/bold]: {result.plan.requires_confirmation}")
        console.print(f"[bold]Safe To Execute[/bold]: {result.plan.safe_to_execute}")
        if result.plan.blocked_reason:
            console.print(f"[bold]Blocked Reason[/bold]: {_safe_console_text(result.plan.blocked_reason)}")
    console.print("[bold]Execution[/bold]: none")


def ai_home_preview(
    project: str,
    text: str | None = None,
    as_json: bool = False,
    show_plan: bool = False,
    adapter_status: bool = False,
    capabilities: bool = False,
    source: str = "text",
) -> None:
    from app.home.service import HomeControlService

    console = Console()
    service = HomeControlService()

    if adapter_status:
        status = service.adapter_status()
        if as_json:
            typer.echo(json.dumps(_json_safe(status), ensure_ascii=False, indent=2))
            return
        for key, value in status.items():
            console.print(f"{key}: {value}")
        return

    if capabilities:
        items = service.list_capabilities()
        if as_json:
            typer.echo(json.dumps(_json_safe(items), ensure_ascii=False, indent=2))
            return
        for item in items:
            console.print(
                f"- {item['capability']} "
                f"(read={item['state_read_supported']}, write={item['state_write_supported']}, "
                f"exec={item['execution_supported']}, dry_run={item['dry_run_supported']})"
            )
        return

    if not text:
        console.print("[red]Home preview icin bir metin belirtmelisin.[/red]")
        raise typer.Exit(1)

    source_enum = _parse_action_source(source)
    plan, result = service.preview_plan(text, source=source_enum)
    payload = {
        "project": project,
        "text": text,
        "plan": asdict(plan) if plan is not None else None,
        "result": asdict(result),
    }
    if as_json:
        typer.echo(json.dumps(_json_safe(payload), ensure_ascii=False, indent=2))
        return

    console.print(f"[bold]Project[/bold]: {project}")
    console.print(f"[bold]Status[/bold]: {result.status.value}")
    console.print(f"[bold]Message[/bold]: {_safe_console_text(result.message)}")
    if show_plan and plan is not None:
        console.print(f"[bold]Plan[/bold]: {_safe_console_text(plan.summary)}")
        console.print(f"[bold]Adapter[/bold]: {plan.adapter_name}")
        console.print(f"[bold]Capability[/bold]: {plan.capability}")
        console.print(f"[bold]State Read[/bold]: {plan.state_read}")
        console.print(f"[bold]State Write[/bold]: {plan.state_write}")
        console.print(f"[bold]Risk[/bold]: {plan.risk_level.value}")
        console.print(f"[bold]Confirmation Required[/bold]: {plan.requires_confirmation}")
        console.print(f"[bold]Safe To Execute[/bold]: {plan.safe_to_execute}")
        if plan.blocked_reason:
            console.print(f"[bold]Blocked Reason[/bold]: {_safe_console_text(plan.blocked_reason)}")
    console.print("[bold]Execution[/bold]: none")


def _panel_operation_payload(project: str, result) -> dict[str, object]:
    return {
        "project": project,
        "status": result.status.value,
        "message": result.message,
        "item": result.item.model_dump(mode="json") if result.item is not None else None,
        "items": [item.model_dump(mode="json") for item in result.items],
        "decision": result.decision.model_dump(mode="json") if result.decision is not None else None,
        "warnings": result.warnings,
        "metadata": result.metadata,
    }


def ai_panel(
    project: str,
    submit: str | None = None,
    list_items: bool = False,
    show: str | None = None,
    approve: str | None = None,
    deny: str | None = None,
    cancel: str | None = None,
    clear: bool = False,
    as_json: bool = False,
    status: str | None = None,
    source: str = "text",
) -> None:
    from app.panel.formatting import format_operation
    from app.panel.service import PermissionPanelService

    console = Console()
    service = PermissionPanelService()
    source_enum = _parse_action_source(source)

    if submit is not None:
        result = service.submit_text(submit, source=source_enum, project_name=project)
    elif list_items:
        result = service.list_items(status=status)
    elif show is not None:
        result = service.show_item(show)
    elif approve is not None:
        result = service.approve_item(approve)
    elif deny is not None:
        result = service.deny_item(deny)
    elif cancel is not None:
        result = service.cancel_item(cancel)
    elif clear:
        result = service.clear_items()
    else:
        console.print("[red]Bir panel islemi secmelisin.[/red]")
        raise typer.Exit(1)

    if as_json:
        typer.echo(json.dumps(_json_safe(_panel_operation_payload(project, result)), ensure_ascii=False, indent=2))
        return

    console.print(format_operation(result))


def ai_reminder(
    project: str,
    text: str | None = None,
    list_items: bool = False,
    cancel: str | None = None,
    as_json: bool = False,
    source: str = "text",
) -> None:
    from app.personal_assistant.reminders import ReminderService

    console = Console()
    service = ReminderService()
    reminder_source = _parse_personal_source(source)

    if list_items:
        result = service.list_reminders()
    elif cancel is not None:
        result = service.cancel_reminder(cancel)
    else:
        if not text:
            console.print("[red]Reminder istegi veya --list/--cancel belirtmelisin.[/red]")
            raise typer.Exit(1)
        result = service.create_reminder(text, source=reminder_source)

    if as_json:
        typer.echo(result.model_dump_json(indent=2))
        return

    console.print(_safe_console_text(service.format_result(result)))


def ai_calendar(
    project: str,
    text: str | None = None,
    list_drafts: bool = False,
    cancel_draft: str | None = None,
    as_json: bool = False,
    source: str = "text",
) -> None:
    from app.personal_assistant.calendar import CalendarService
    from app.personal_assistant.models import CalendarOperation
    from app.personal_assistant.parser import parse_calendar_request

    console = Console()
    service = CalendarService()
    reminder_source = _parse_personal_source(source)

    if list_drafts:
        result = service.list_event_drafts()
    elif cancel_draft is not None:
        result = service.cancel_event_draft(cancel_draft)
    else:
        if not text:
            console.print("[red]Calendar istegi veya --list-drafts/--cancel-draft belirtmelisin.[/red]")
            raise typer.Exit(1)
        operation, _ = parse_calendar_request(text)
        if operation is CalendarOperation.QUERY:
            result = service.query_calendar(text, source=reminder_source)
        elif operation is CalendarOperation.DRAFT_EVENT:
            result = service.create_event_draft(text, source=reminder_source)
        else:
            result = service.query_calendar(text, source=reminder_source)

    if as_json:
        typer.echo(result.model_dump_json(indent=2))
        return

    console.print(_safe_console_text(service.format_result(result)))


def ai_notification_preview(
    project: str,
    title: str,
    body: str,
    channel: str = "cli",
    as_json: bool = False,
) -> None:
    from app.personal_assistant.models import NotificationChannel
    from app.personal_assistant.notifications import NotificationService

    console = Console()
    service = NotificationService()
    try:
        channel_enum = NotificationChannel(channel)
    except ValueError as exc:
        raise typer.BadParameter("channel must be one of: cli, future_desktop, future_os, future_mobile") from exc

    result = service.build_notification_preview(title=title, body=body, channel=channel_enum)
    if as_json:
        typer.echo(result.model_dump_json(indent=2))
        return

    if result.notification is not None:
        console.print(_safe_console_text(service.format_notification(result.notification)))
    console.print(_safe_console_text(result.message))


def ai_chat(
    user_text: str,
    project: str,
    source: str = "text",
    session_id: str | None = None,
    as_json: bool = False,
    show_state: bool = False,
    reset_session: bool = False,
) -> None:
    """Run the conversational loop MVP for ATLAS."""
    from app.conversation.loop import ConversationLoop
    from app.actions.types import ActionSource
    
    console = Console()
    
    # Map source
    try:
        source_enum = ActionSource(source)
    except ValueError:
        source_enum = ActionSource.TEXT
        
    loop = ConversationLoop()
    
    if reset_session and session_id:
        loop.reset_session(session_id)
        if not as_json:
            console.print(f"[green]Session {session_id} reset.[/green]")
            return
            
    response = loop.handle_text(
        message=user_text,
        project_name=project,
        session_id=session_id,
        source=source_enum
    )
    
    if as_json:
        print(response.model_dump_json(indent=2))
        return
        
    console.print(f"[bold]ATLAS[/bold]: {response.assistant_message}")
    
    if show_state:
        state = loop.get_state(response.session_id)
        console.print(f"\n[dim]State: intent={state.last_intent}, action={state.last_action}[/dim]")
        console.print(f"[dim]Pending clarification: {state.pending_clarification}[/dim]")
        console.print(f"[dim]Pending confirmation: {state.pending_confirmation}[/dim]")

def ai_memory_personal(
    project: str,
    text: str,
    json_output: bool = False,
    show_all: bool = False,
    clear: bool = False,
    memory_type_str: str | None = None,
    session_id: str | None = None,
):
    from app.personal_memory.service import PersonalMemoryService
    from app.personal_memory.models import MemoryType, MemoryOperationStatus
    from rich.console import Console
    import json
    
    console = Console()
    service = PersonalMemoryService()
    
    m_type = MemoryType.UNKNOWN
    if memory_type_str:
        try:
            m_type = MemoryType(memory_type_str)
        except ValueError:
            pass
            
    if clear:
        count = service.store.clear(m_type if m_type != MemoryType.UNKNOWN else None)
        if json_output:
            print(json.dumps({"status": "cleared", "count": count}))
        else:
            console.print(f"Hafıza temizlendi. (Silinen: {count})")
        return
        
    if show_all:
        res = service.show(m_type)
        if json_output:
            print(res.model_dump_json(indent=2))
        else:
            console.print(res.message)
        return
        
    res = service.handle_text(text)
    if json_output:
        print(res.model_dump_json(indent=2))
    else:
        if res.status == MemoryOperationStatus.BLOCKED:
            console.print(f"[red]BLOCKED[/red]: {res.message}")
            if res.blocked_reason:
                console.print(f"[dim]{res.blocked_reason}[/dim]")
        else:
            console.print(f"[green]SUCCESS[/green]: {res.message}")

def ai_routine(
    project: str,
    text: str | None = None,
    json_output: bool = False,
    list_routines: bool = False,
    show_preview: bool = False,
    source: str = "text"
):
    from app.routines.engine import RoutineEngine
    from app.routines.service import RoutineService
    from app.actions.types import ActionSource
    from rich.console import Console
    import json
    
    console = Console()
    engine = RoutineEngine()
    service = RoutineService()
    
    if list_routines:
        routines = engine.list_routines()
        if json_output:
            print(json.dumps([r.model_dump() for r in routines], default=str))
        else:
            for r in routines:
                console.print(f"- [bold]{r.display_name}[/bold] ({len(r.steps)} steps, risk: {r.risk_level})")
        return

    if not text:
        console.print("[red]Rutin ismi belirtmediniz.[/red]")
        return

    routine_name, _ = service.parse_routine_request(text)
    if not routine_name:
        routine_name = text

    if show_preview:
        src_enum = ActionSource(source) if source in [e.value for e in ActionSource] else ActionSource.TEXT
        preview = engine.preview_routine(routine_name, source=src_enum)
        if json_output:
            print(preview.model_dump_json(indent=2))
        else:
            console.print(f"[bold]Routine Preview: {preview.routine_name}[/bold]")
            console.print(f"Risk: {preview.risk_level}, Conf Req: {preview.requires_confirmation}")
            console.print(f"Blocked: {preview.blocked}")
            for step in preview.steps:
                console.print(f"  - Step: {step.label} ({step.action_type})")
        return

    res = service.handle_text(text)
    if json_output:
        if hasattr(res, "model_dump_json"):
            print(res.model_dump_json(indent=2))
        else:
            print(json.dumps({"message": service.format_response(res)}, ensure_ascii=False, indent=2))
    else:
        formatted = service.format_response(res)
        status_value = getattr(getattr(res, "status", None), "value", None)
        if status_value == "blocked":
            console.print(f"[red]BLOCKED[/red]: {formatted}")
        elif status_value == "awaiting_confirmation":
            console.print(f"[yellow]CONFIRMATION REQUIRED[/yellow]: {formatted}")
        else:
            console.print(f"[green]SUCCESS[/green]: {formatted}")


def ai_voice(
    project: str,
    mock_transcript: str | None = None,
    audio_path: str | None = None,
    language: str = "tr",
    session_id: str | None = None,
    speak: bool = False,
    as_json: bool = False,
    show_transcript: bool = False,
    show_safety: bool = False,
) -> None:
    from app.voice.mock_adapters import MockSTTAdapter, MockTTSAdapter
    from app.voice.models import VoicePipelineRequest, VoiceSource
    from app.voice.pipeline import VoicePipeline

    console = Console()
    if not mock_transcript and not audio_path:
        console.print("[red]Mock transcript veya audio path belirtmelisin.[/red]")
        raise typer.Exit(1)

    source = VoiceSource.MOCK_TRANSCRIPT if mock_transcript else VoiceSource.AUDIO_FILE
    pipeline = VoicePipeline(stt_adapter=MockSTTAdapter(), tts_adapter=MockTTSAdapter())
    result = pipeline.handle(
        VoicePipelineRequest(
            project_name=project,
            mock_transcript=mock_transcript,
            audio_path=audio_path,
            language=language,
            session_id=session_id,
            speak=speak,
            source=source,
        )
    )

    if as_json:
        typer.echo(json.dumps(_json_safe(_voice_pipeline_payload(project, result)), ensure_ascii=False, indent=2))
        return

    console.print(f"[bold]Project[/bold]: {project}")
    console.print(f"[bold]Source[/bold]: {result.metadata.get('source', source.value)}")
    if show_transcript:
        console.print(f"[bold]Transcript[/bold]: {_safe_console_text(result.transcript.text or '(empty)')}")
        console.print(f"[bold]Transcript Confidence[/bold]: {result.transcript.confidence}")
    console.print(f"[bold]Response[/bold]: {_safe_console_text(result.conversation_response.assistant_message if result.conversation_response else 'none')}")
    console.print(f"[bold]Response Type[/bold]: {result.conversation_response.response_type.value if result.conversation_response else 'none'}")

    if show_safety:
        console.print("[bold]Safety[/bold]")
        console.print(f"- audio_retained: {result.audio_retained}")
        console.print(f"- microphone_used: {result.microphone_used}")
        console.print(f"- wake_word_used: {result.wake_word_used}")
        console.print(f"- execution_attempted: {result.execution_attempted}")
        for warning in result.safety_warnings:
            console.print(f"- warning: {_safe_console_text(warning)}")

    if speak and result.tts_result is not None:
        console.print("[bold]TTS[/bold]")
        console.print(f"- engine: {result.tts_result.engine}")
        console.print(f"- success: {result.tts_result.success}")
        console.print(f"- spoken: {result.tts_result.spoken}")
        for warning in result.tts_result.warnings:
            console.print(f"- warning: {_safe_console_text(warning)}")

    console.print("[bold]Execution[/bold]: none")


def _conversation_response_payload(response) -> dict[str, object] | None:
    if response is None:
        return None
    return {
        "session_id": response.session_id,
        "user_message": response.user_message,
        "assistant_message": response.assistant_message,
        "response_type": response.response_type.value,
        "intent": response.intent,
        "action_candidate": asdict(response.action_candidate) if response.action_candidate is not None else None,
        "permission_decision": asdict(response.permission_decision) if response.permission_decision is not None else None,
        "pc_plan": response.pc_plan.model_dump() if response.pc_plan is not None else None,
        "clarification_required": response.clarification_required,
        "confirmation_required": response.confirmation_required,
        "blocked": response.blocked,
        "warnings": response.warnings,
        "suggestions": response.suggestions,
        "audit_metadata": response.audit_metadata,
        "metadata": response.metadata,
    }


def _voice_pipeline_payload(project: str, result) -> dict[str, object]:
    return {
        "project": project,
        "transcript": result.transcript.model_dump(),
        "conversation_response": _conversation_response_payload(result.conversation_response),
        "tts_result": result.tts_result.model_dump() if result.tts_result is not None else None,
        "safety_warnings": result.safety_warnings,
        "audio_retained": result.audio_retained,
        "microphone_used": result.microphone_used,
        "wake_word_used": result.wake_word_used,
        "execution_attempted": result.execution_attempted,
        "metadata": result.metadata,
    }
