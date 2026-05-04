from __future__ import annotations

from pathlib import Path

from app.config.loader import load_and_validate_configs


def test_load_and_validate_configs_ok(isolated_atlas: Path) -> None:
    root = isolated_atlas
    settings, reg, safety, mcp = load_and_validate_configs(root / "configs")
    assert settings.root == root.resolve()
    assert reg.projects[0].name == "Demo"
    assert mcp.mcpServers.get("workspace-filesystem")
