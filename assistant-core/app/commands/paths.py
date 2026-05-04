"""paths — print resolved ATLAS paths."""

from __future__ import annotations

import typer
from rich.console import Console

from app.paths import (
    get_atlas_root,
    get_configs_dir,
    get_logs_dir,
    get_memory_db_path,
    get_templates_dir,
    get_workspace_dir,
)


def paths_cmd() -> None:
    console = Console()
    console.print(f"ATLAS root:       {get_atlas_root()}")
    console.print(f"workspace:       {get_workspace_dir()}")
    console.print(f"configs:         {get_configs_dir()}")
    console.print(f"logs:            {get_logs_dir()}")
    console.print(f"templates:       {get_templates_dir()}")
    console.print(f"memory_db:       {get_memory_db_path()}")
