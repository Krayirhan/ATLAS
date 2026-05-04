from __future__ import annotations

import json
from pathlib import Path

from app.mcp.generator import generate_all, plan_mcp_generate


def test_mcp_generate_dry_run_writes_no_files(isolated_atlas: Path) -> None:
    root = isolated_atlas
    cfg = root / "configs"
    gen = cfg / "generated"
    planned = plan_mcp_generate(config_root=cfg, target="cursor")
    assert len(planned) == 1
    path, content = planned[0]
    assert path.name == "cursor.mcp.json"
    assert "@modelcontextprotocol/server-filesystem" in content
    low = content.lower().replace("\\\\", "\\")
    assert "d:\\atlas" not in low and "d:/atlas" not in low
    assert "workspace" in low

    generate_all(config_root=cfg, target="all", dry_run=True)
    assert not gen.exists() or not (gen / "cursor.mcp.json").is_file()


def test_mcp_generate_writes_when_not_dry_run(isolated_atlas: Path) -> None:
    root = isolated_atlas
    cfg = root / "configs"
    generate_all(config_root=cfg, target="cursor", dry_run=False)
    out = cfg / "generated" / "cursor.mcp.json"
    assert out.is_file()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "mcpServers" in data


def test_mcp_plan_workspace_path_matches_policy_workspace(isolated_atlas: Path) -> None:
    root = isolated_atlas
    cfg = root / "configs"
    planned = plan_mcp_generate(config_root=cfg, target="cursor")
    _, content = planned[0]
    data = json.loads(content)
    args = data["mcpServers"]["workspace-filesystem"]["args"]
    path_arg = args[-1]
    assert Path(path_arg).resolve() == (root / "workspace").resolve()


def test_mcp_plan_not_full_disk_root_users(isolated_atlas: Path) -> None:
    """Workspace MCP arg must be the ATLAS workspace folder, not a bare C:\\Users root."""
    root = isolated_atlas
    planned = plan_mcp_generate(config_root=root / "configs", target="cursor")
    _, content = planned[0]
    data = json.loads(content)
    args = data["mcpServers"]["workspace-filesystem"]["args"]
    path_arg = str(args[-1]).lower().replace("\\\\", "\\")
    assert path_arg.rstrip("\\").endswith("workspace")
    assert path_arg.rstrip("\\") != "c:\\users"
