"""Pytest fixtures for isolated ATLAS_ROOT trees."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Generator

import pytest


def _write_minimal_atlas_tree(root: Path) -> None:
    (root / "assistant-core").mkdir(parents=True)
    (root / "workspace" / "memory").mkdir(parents=True)
    (root / "workspace" / "knowledge-base").mkdir(parents=True)
    (root / "workspace" / "outputs").mkdir(parents=True)
    (root / "workspace" / "notebooklm-exports").mkdir(parents=True)
    (root / "configs").mkdir()
    (root / "mcp-servers").mkdir()
    (root / "backups").mkdir()
    (root / "logs" / "tool-calls").mkdir(parents=True)
    (root / "logs" / "sessions").mkdir(parents=True)
    (root / "logs" / "errors").mkdir(parents=True)
    (root / "templates").mkdir()

    ws = root / "workspace"
    ws_resolved = str(ws.resolve())

    (root / "configs" / "assistant.settings.json").write_text(
        json.dumps(
            {
                "root": str(root),
                "workspace_root": str(ws),
                "memory_db": str(ws / "memory" / "assistant.db"),
                "default_shell": "powershell",
                "log_level": "info",
                "environment": "local",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "configs" / "project-registry.json").write_text(
        json.dumps(
            {
                "projects": [
                    {
                        "name": "Demo",
                        "type": "python-cli",
                        "root": str(root / "assistant-core"),
                        "knowledge": "",
                        "build_command": "",
                        "test_command": "python -m pytest -q",
                        "lint_command": "",
                        "forbidden_changes": [],
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "configs" / "safety-policy.json").write_text(
        json.dumps(
            {
                "allowed_workspace_roots": [ws_resolved],
                "blocked_paths": ["C:\\Users", "D:\\ATLAS"],
                "blocked_file_patterns": [".env", "*.pem", "id_rsa", "id_ed25519"],
                "blocked_commands": [
                    "git reset --hard",
                    "git clean -fd",
                    "git push --force",
                    "Remove-Item -Recurse",
                    "format",
                ],
                "approval_required_commands": ["pip install"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    mcp = {
        "mcpServers": {
            "workspace-filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", ws_resolved],
            },
            "project-memory-mcp": {
                "command": "python",
                "args": [str((root / "mcp-servers" / "project-memory-mcp" / "server.py").resolve())],
            },
        }
    }
    (root / "mcp-servers" / "project-memory-mcp").mkdir(parents=True)
    (root / "mcp-servers" / "project-memory-mcp" / "server.py").write_text("# stub\n", encoding="utf-8")
    (root / "configs" / "mcp.master.json").write_text(json.dumps(mcp) + "\n", encoding="utf-8")


@pytest.fixture
def isolated_atlas(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Generator[Path, None, None]:
    root = tmp_path / "atlas"
    _write_minimal_atlas_tree(root)
    monkeypatch.setenv("ATLAS_ROOT", str(root))
    yield root
