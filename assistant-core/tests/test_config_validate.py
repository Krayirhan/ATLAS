from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.config.loader import ConfigError, load_and_validate_configs, load_project_registry


def test_load_and_validate_configs_ok(isolated_atlas: Path) -> None:
    root = isolated_atlas
    settings, reg, safety, mcp = load_and_validate_configs(root / "configs")
    assert settings.root == root.resolve()
    assert reg.projects[0].name == "Demo"
    assert mcp.mcpServers.get("workspace-filesystem")


def test_duplicate_project_name_rejected(isolated_atlas: Path) -> None:
    root = isolated_atlas
    ac = root / "assistant-core"
    dup = {
        "projects": [
            {
                "name": "Dup",
                "type": "python-cli",
                "root": str(ac),
                "knowledge": "",
                "build_command": "",
                "test_command": "",
                "lint_command": "",
                "forbidden_changes": [],
            },
            {
                "name": "Dup",
                "type": "python-cli",
                "root": str(ac),
                "knowledge": "",
                "build_command": "",
                "test_command": "",
                "lint_command": "",
                "forbidden_changes": [],
            },
        ]
    }
    (root / "configs" / "project-registry.json").write_text(json.dumps(dup) + "\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="Duplicate project name"):
        load_and_validate_configs(root / "configs")


def test_unknown_project_type_rejected(isolated_atlas: Path) -> None:
    root = isolated_atlas
    ac = root / "assistant-core"
    bad = {
        "projects": [
            {
                "name": "X",
                "type": "unknown-stack-9000",
                "root": str(ac),
                "knowledge": "",
                "build_command": "",
                "test_command": "",
                "lint_command": "",
                "forbidden_changes": [],
            }
        ]
    }
    (root / "configs" / "project-registry.json").write_text(json.dumps(bad) + "\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_and_validate_configs(root / "configs")


def test_python_cli_project_type_accepted(isolated_atlas: Path) -> None:
    root = isolated_atlas
    reg = load_project_registry(root / "configs")
    assert reg.projects[0].type == "python-cli"


def test_atlas_style_registry_validates(isolated_atlas: Path) -> None:
    root = isolated_atlas
    kb = root / "workspace" / "knowledge-base" / "ATLAS"
    kb.mkdir(parents=True, exist_ok=True)
    (kb / "00-project-summary.md").write_text("# ok\n", encoding="utf-8")
    reg = {
        "projects": [
            {
                "name": "ATLAS",
                "type": "python-cli",
                "root": str(root.resolve()),
                "knowledge": str(kb.resolve()),
                "build_command": "",
                "test_command": "python -m pytest -q",
                "lint_command": "",
                "command_workdir": str((root / "assistant-core").resolve()),
                "forbidden_changes": [],
            }
        ]
    }
    (root / "configs" / "project-registry.json").write_text(json.dumps(reg) + "\n", encoding="utf-8")
    load_and_validate_configs(root / "configs")
