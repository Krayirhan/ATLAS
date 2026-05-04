"""Models for MCP config generation."""

from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field


class MCPServerModel(BaseModel):
    command: str
    args: List[str] = Field(default_factory=list)


class MCPMasterModel(BaseModel):
    mcpServers: Dict[str, MCPServerModel]
