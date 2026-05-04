"""Pydantic models for ATLAS JSON configs."""

from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, field_validator

from app.mcp.models import MCPMasterModel
from app.projects.types import validate_project_type


class OllamaSettings(BaseModel):
    base_url: str = "http://localhost:11434"
    default_model: str = "qwen2.5:7b"
    timeout_seconds: int = 300
    stream: bool = False
    keep_alive: str = "30m"


class AISettings(BaseModel):
    default_provider: str = "ollama"
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)


class AssistantSettings(BaseModel):
    """Runtime paths are normalized against discovered ATLAS root in loader."""

    root: Path
    workspace_root: Path
    memory_db: Path
    default_shell: str = "powershell"
    log_level: str = "info"
    environment: str = "local"
    ai: AISettings = Field(default_factory=AISettings)

    @field_validator("root", "workspace_root", "memory_db", mode="before")
    @classmethod
    def _to_path(cls, v: object) -> Path:
        return Path(v) if not isinstance(v, Path) else v


class ProjectEntry(BaseModel):
    name: str
    type: str
    root: Path
    knowledge: Path | str = ""
    build_command: str = ""
    test_command: str = ""
    lint_command: str = ""
    status_command: str = ""
    command_workdir: Path | str = ""
    forbidden_changes: List[str] = Field(default_factory=list)

    @field_validator("root", mode="before")
    @classmethod
    def _root_path(cls, v: object) -> Path:
        return Path(v) if not isinstance(v, Path) else v

    @field_validator("type")
    @classmethod
    def _type_allowed(cls, v: object) -> str:
        return validate_project_type(str(v))

    @field_validator("knowledge", mode="before")
    @classmethod
    def _knowledge_path(cls, v: object) -> Path | str:
        if v is None or v == "":
            return ""
        return Path(v) if not isinstance(v, Path) else v

    @field_validator("command_workdir", mode="before")
    @classmethod
    def _command_workdir_path(cls, v: object) -> Path | str:
        if v is None or v == "":
            return ""
        return Path(v) if not isinstance(v, Path) else v


class ProjectRegistryModel(BaseModel):
    projects: List[ProjectEntry] = Field(default_factory=list)


class SafetyPolicyModel(BaseModel):
    allowed_workspace_roots: List[str] = Field(default_factory=list)
    blocked_paths: List[str] = Field(default_factory=list)
    blocked_file_patterns: List[str] = Field(default_factory=list)
    blocked_commands: List[str] = Field(default_factory=list)
    approval_required_commands: List[str] = Field(default_factory=list)


# Re-export MCP master model for single import site
__all__ = [
    "AISettings",
    "AssistantSettings",
    "OllamaSettings",
    "ProjectEntry",
    "ProjectRegistryModel",
    "SafetyPolicyModel",
    "MCPMasterModel",
]
