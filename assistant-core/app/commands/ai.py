"""CLI commands for the read-only AI layer."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

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
