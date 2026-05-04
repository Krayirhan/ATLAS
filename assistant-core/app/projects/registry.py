"""Read/write project-registry.json."""

from __future__ import annotations

import json
from pathlib import Path

from app.config.loader import ConfigError, load_project_registry, remap_stale_atlas_path
from app.config.models import ProjectEntry, ProjectRegistryModel
from app.paths import get_atlas_root, get_configs_dir


def registry_path(config_root: Path | None = None) -> Path:
    return (config_root or get_configs_dir()) / "project-registry.json"


def save_registry(model: ProjectRegistryModel, config_root: Path | None = None) -> None:
    path = registry_path(config_root)
    data = model.model_dump(mode="json")
    # Pydantic v2 Path -> str in json mode
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def add_project(entry: ProjectEntry, config_root: Path | None = None) -> None:
    reg = load_project_registry(config_root)
    if any(p.name == entry.name for p in reg.projects):
        raise ConfigError(f"Project already exists: {entry.name}")
    if not entry.root.exists():
        raise ConfigError(f"Project root does not exist: {entry.root}")
    reg.projects.append(entry)
    save_registry(reg, config_root)


def get_project(name: str, config_root: Path | None = None) -> ProjectEntry | None:
    reg = load_project_registry(config_root)
    for p in reg.projects:
        if p.name == name:
            return p
    return None


def validate_project(name: str, config_root: Path | None = None) -> list[str]:
    issues: list[str] = []
    p = get_project(name, config_root)
    if not p:
        issues.append("unknown project")
        return issues
    if not p.root.exists():
        issues.append(f"root missing: {p.root}")
    if p.knowledge and str(p.knowledge).strip():
        kp = Path(str(p.knowledge))
        if not kp.is_dir():
            issues.append(f"knowledge path not a directory: {kp}")
    if p.command_workdir and str(p.command_workdir).strip():
        wd = Path(str(p.command_workdir))
        if not wd.is_dir():
            issues.append(f"command_workdir not a directory: {wd}")
    return issues
