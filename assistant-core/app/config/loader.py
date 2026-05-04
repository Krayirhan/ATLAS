"""Load and validate configs; paths are anchored to discovered ATLAS root."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple

from pydantic import ValidationError

from app.config.models import (
    AssistantSettings,
    MCPMasterModel,
    ProjectRegistryModel,
    SafetyPolicyModel,
)
from app.paths import get_atlas_root, get_configs_dir, get_memory_db_path, get_workspace_dir


class ConfigError(Exception):
    """Validation or IO error for ATLAS configs."""


def _read_json(path: Path) -> dict:
    if not path.is_file():
        raise ConfigError(f"Missing config file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in {path}: {exc}") from exc


def _is_under(parent: Path, child: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def load_assistant_settings(config_root: Path | None = None) -> AssistantSettings:
    root = get_atlas_root()
    cfg_dir = config_root or get_configs_dir()
    raw = _read_json(cfg_dir / "assistant.settings.json")
    # Canonical paths from repo layout (ignore stale drive letters in JSON)
    data = {
        "root": root,
        "workspace_root": get_workspace_dir(),
        "memory_db": get_memory_db_path(),
        "default_shell": raw.get("default_shell", "powershell"),
        "log_level": raw.get("log_level", "info"),
        "environment": raw.get("environment", "local"),
    }
    model = AssistantSettings.model_validate(data)
    if not _is_under(model.root, model.workspace_root):
        raise ConfigError("workspace_root must be under ATLAS root")
    if not _is_under(model.root, model.memory_db):
        raise ConfigError("memory_db must be under ATLAS root")
    return model


def remap_stale_atlas_path(path: Path, atlas_root: Path) -> Path:
    """If JSON used D:/ATLAS but repo lives on another drive, prefer the live ATLAS root."""
    atlas_root = atlas_root.resolve()
    sp = path.as_posix()
    for old in ("D:/ATLAS", "d:/ATLAS"):
        if sp.lower().startswith(old.lower()):
            suffix = sp[len(old) :].lstrip("/\\")
            candidate = (atlas_root / suffix).resolve()
            if candidate.exists():
                return candidate
    if path.exists():
        return path.resolve()
    return path


def load_project_registry(config_root: Path | None = None) -> ProjectRegistryModel:
    cfg_dir = config_root or get_configs_dir()
    raw = _read_json(cfg_dir / "project-registry.json")
    atlas = get_atlas_root()
    for p in raw.get("projects", []):
        if "root" in p:
            p["root"] = str(remap_stale_atlas_path(Path(p["root"]), atlas))
        k = p.get("knowledge")
        if k:
            p["knowledge"] = str(remap_stale_atlas_path(Path(str(k)), atlas))
        cw = p.get("command_workdir")
        if cw:
            p["command_workdir"] = str(remap_stale_atlas_path(Path(str(cw)), atlas))
    try:
        return ProjectRegistryModel.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(f"Invalid project-registry.json: {exc}") from exc


def load_safety_policy(config_root: Path | None = None) -> SafetyPolicyModel:
    cfg_dir = config_root or get_configs_dir()
    raw = _read_json(cfg_dir / "safety-policy.json")
    atlas = get_atlas_root()
    roots = []
    for r in raw.get("allowed_workspace_roots", []):
        roots.append(str(remap_stale_atlas_path(Path(r), atlas)))
    raw["allowed_workspace_roots"] = roots
    return SafetyPolicyModel.model_validate(raw)


def load_mcp_master(config_root: Path | None = None) -> MCPMasterModel:
    cfg_dir = config_root or get_configs_dir()
    raw = _read_json(cfg_dir / "mcp.master.json")
    return MCPMasterModel.model_validate(raw)


def load_and_validate_configs(config_root: Path | None = None) -> Tuple[
    AssistantSettings,
    ProjectRegistryModel,
    SafetyPolicyModel,
    MCPMasterModel,
]:
    """Load all core configs; raises ConfigError on failure."""
    settings = load_assistant_settings(config_root)
    registry = load_project_registry(config_root)
    safety = load_safety_policy(config_root)
    mcp = load_mcp_master(config_root)
    names = [p.name for p in registry.projects]
    if len(names) != len(set(names)):
        raise ConfigError("Duplicate project name in project-registry.json")
    for p in registry.projects:
        if not p.root.exists():
            raise ConfigError(f"Project root does not exist: {p.name} -> {p.root}")
    _validate_mcp_workspace_filesystem(mcp, settings.workspace_root)
    return settings, registry, safety, mcp


def _validate_mcp_workspace_filesystem(mcp: MCPMasterModel, workspace_root: Path) -> None:
    fs = mcp.mcpServers.get("workspace-filesystem")
    if not fs:
        return
    args = fs.args or []
    joined = " ".join(str(a) for a in args)
    if "@modelcontextprotocol/server-filesystem" not in joined:
        raise ConfigError("workspace-filesystem MCP must use @modelcontextprotocol/server-filesystem")
    candidate: Path | None = None
    for arg in reversed(args):
        if isinstance(arg, str) and not arg.startswith("-") and "@" not in arg:
            candidate = Path(arg)
            break
    if candidate is None:
        raise ConfigError("workspace-filesystem MCP args must include a workspace directory path")
    resolved = candidate.expanduser().resolve()
    expected = workspace_root.resolve()
    if resolved != expected:
        raise ConfigError(
            f"workspace-filesystem must expose only ATLAS workspace ({expected}); config has {resolved}"
        )
    low = joined.lower().replace("/", "\\")
    if "d:\\atlas" in low:
        raise ConfigError("workspace-filesystem must not reference D:\\ATLAS")
