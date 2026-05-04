"""Resolve ATLAS monorepo root and standard subpaths (portable: E:\\ vs D:\\)."""

from __future__ import annotations

import os
from pathlib import Path


def get_atlas_root() -> Path:
    """ATLAS repo root (parent of assistant-core). Override with ATLAS_ROOT env."""
    env = os.environ.get("ATLAS_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    # assistant-core/app/paths.py -> parents[2] == ATLAS root
    return Path(__file__).resolve().parents[2]


def get_configs_dir() -> Path:
    return get_atlas_root() / "configs"


def get_workspace_dir() -> Path:
    return get_atlas_root() / "workspace"


def get_logs_dir() -> Path:
    return get_atlas_root() / "logs"


def get_templates_dir() -> Path:
    return get_atlas_root() / "templates"


def get_memory_db_path() -> Path:
    return get_workspace_dir() / "memory" / "assistant.db"
