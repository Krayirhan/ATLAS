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
