"""CLI command for configuration validation."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from app.config.loader import ConfigError, load_and_validate_configs
from app.paths import get_configs_dir


def validate_configs(config_root: Path | None = None) -> None:
    console = Console()
    root = config_root or get_configs_dir()
    try:
        load_and_validate_configs(config_root=root)
    except ConfigError as exc:
        console.print(f"[red]Config validation failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print("[green]Configuration validation successful.[/green]")
