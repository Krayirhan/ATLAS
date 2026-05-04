from __future__ import annotations

import os
from pathlib import Path

from typer.testing import CliRunner

from app.cli import app


def test_doctor_paths_config_smoke(monkeypatch, tmp_path: Path) -> None:
    """CLI smoke: doctor, paths, config validate (isolated ATLAS_ROOT)."""
    root = tmp_path / "atlas"
    (root / "assistant-core").mkdir(parents=True)
    (root / "workspace").mkdir()
    for sub in ("memory", "knowledge-base", "outputs", "notebooklm-exports"):
        (root / "workspace" / sub).mkdir(parents=True)
    (root / "configs").mkdir()
    (root / "mcp-servers").mkdir()
    (root / "backups").mkdir()
    (root / "logs" / "tool-calls").mkdir(parents=True)
    (root / "templates").mkdir()
    monkeypatch.setenv("ATLAS_ROOT", str(root))
    (root / "configs" / "assistant.settings.json").write_text(
        '{"root": "X:/STALE", "workspace_root": "X:/STALE/workspace", '
        '"memory_db": "X:/STALE/workspace/memory/assistant.db", '
        '"default_shell": "powershell", "log_level": "info", "environment": "local"}\n',
        encoding="utf-8",
    )
    (root / "configs" / "project-registry.json").write_text(
        '{"projects": [{"name": "Demo", "type": "python-cli", "root": "'
        + str(root / "assistant-core").replace("\\", "/")
        + '", "knowledge": "", "build_command": "", "test_command": "", '
        '"lint_command": "", "forbidden_changes": []}]}\n',
        encoding="utf-8",
    )
    (root / "configs" / "safety-policy.json").write_text(
        '{"allowed_workspace_roots": ["'
        + str(root / "workspace").replace("\\", "/")
        + '"], "blocked_paths": [], "blocked_file_patterns": [], '
        '"blocked_commands": ["format"], "approval_required_commands": []}\n',
        encoding="utf-8",
    )
    (root / "configs" / "mcp.master.json").write_text(
        '{"mcpServers": {"workspace-filesystem": {"command": "npx", '
        '"args": ["-y", "@modelcontextprotocol/server-filesystem", "'
        + str(root / "workspace").replace("\\", "/")
        + '"]}}}\n',
        encoding="utf-8",
    )
    runner = CliRunner()
    for cmd in [["doctor"], ["paths"], ["config", "validate"]]:
        r = runner.invoke(app, cmd, env={**os.environ, "ATLAS_ROOT": str(root)})
        assert r.exit_code == 0, r.output
