"""Generate Cursor, VS Code, and Codex MCP configs from mcp.master.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from app.config.loader import load_assistant_settings, load_mcp_master
from app.paths import get_configs_dir


def _workspace_filesystem_args(workspace: Path) -> List[str]:
    return ["-y", "@modelcontextprotocol/server-filesystem", str(workspace.resolve())]


def _patch_master_workspace(mcp_data: dict, workspace: Path) -> dict:
    """Ensure workspace-filesystem points at this machine's workspace."""
    out = json.loads(json.dumps(mcp_data))
    servers = out.get("mcpServers") or {}
    fs = servers.get("workspace-filesystem")
    if fs and isinstance(fs.get("args"), list):
        fs["args"] = _workspace_filesystem_args(workspace)
    return out


def _patch_mcp_script_paths(mcp_data: dict, atlas_root: Path) -> None:
    """Point bundled MCP helper scripts at the current ATLAS root."""
    servers = mcp_data.get("mcpServers") or {}
    mapping = {
        "project-memory-mcp": atlas_root / "mcp-servers" / "project-memory-mcp" / "server.py",
        "safe-terminal-mcp": atlas_root / "mcp-servers" / "safe-terminal-mcp" / "server.py",
    }
    for key, script in mapping.items():
        spec = servers.get(key)
        if not spec or spec.get("command") != "python":
            continue
        args = spec.get("args")
        if not isinstance(args, list):
            continue
        for i, arg in enumerate(args):
            if isinstance(arg, str) and arg.endswith(".py") and "server.py" in arg:
                spec["args"][i] = str(script.resolve())
                break


def plan_mcp_generate(
    config_root: Path | None = None,
    target: str | None = None,
) -> List[tuple[Path, str]]:
    """Build (path, content) pairs for generated MCP configs without writing."""
    settings = load_assistant_settings(config_root)
    load_mcp_master(config_root)
    cfg_dir = config_root or get_configs_dir()
    gen_dir = cfg_dir / "generated"

    raw_master = json.loads((cfg_dir / "mcp.master.json").read_text(encoding="utf-8-sig"))
    patched = _patch_master_workspace(raw_master, settings.workspace_root)
    _patch_mcp_script_paths(patched, settings.root.resolve())

    cursor_path = gen_dir / "cursor.mcp.json"
    cursor_content = json.dumps(patched, indent=2) + "\n"

    vscode_payload = {"servers": patched.get("mcpServers", {})}
    vscode_path = gen_dir / "vscode.mcp.json"
    vscode_content = json.dumps(vscode_payload, indent=2) + "\n"

    codex_lines = ["[mcp_servers]"]
    for name, spec in patched.get("mcpServers", {}).items():
        cmd = spec.get("command", "")
        args = spec.get("args", [])
        args_repr = json.dumps(args)
        codex_lines.append(f"{name}.command = {json.dumps(cmd)}")
        codex_lines.append(f"{name}.args = {args_repr}")
    codex_path = gen_dir / "codex.config.toml"
    codex_content = "\n".join(codex_lines) + "\n"

    out: List[tuple[Path, str]] = [
        (cursor_path, cursor_content),
        (vscode_path, vscode_content),
        (codex_path, codex_content),
    ]
    t = (target or "all").lower().strip()
    mapping: dict[str, List[tuple[Path, str]]] = {
        "cursor": [out[0]],
        "vscode": [out[1]],
        "codex": [out[2]],
        "all": out,
    }
    if t not in mapping:
        raise ValueError(f"Unknown MCP generate target: {target}")
    return mapping[t]


def generate_all(
    config_root: Path | None = None,
    target: str | None = None,
    dry_run: bool = False,
) -> List[Path]:
    planned = plan_mcp_generate(config_root=config_root, target=target or "all")
    paths: List[Path] = []
    for path, content in planned:
        paths.append(path)
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    return paths


def list_servers(config_root: Path | None = None) -> List[str]:
    master = load_mcp_master(config_root)
    return list(master.mcpServers.keys())
