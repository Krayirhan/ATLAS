"""CLI commands for the read-only AI layer."""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from app.agents.memory_agent import MemoryAgent
from app.agents.models import ProjectQARequest
from app.agents.project_qa_agent import ProjectQAAgent
from app.ai.context_loader import AIContextError
from app.ai.models import AIRequest
from app.ai.providers.base import AIProviderError
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.service import AIService


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
        console.print(
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
    console.print(result.answer)
