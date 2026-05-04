from __future__ import annotations

import json
from pathlib import Path

from app.config.loader import load_project_registry
from app.projects import registry as reg


def test_validate_project_command_workdir(isolated_atlas: Path) -> None:
    root = isolated_atlas
    data = json.loads((root / "configs" / "project-registry.json").read_text(encoding="utf-8"))
    data["projects"][0]["command_workdir"] = str(root / "missing-dir")
    (root / "configs" / "project-registry.json").write_text(json.dumps(data) + "\n", encoding="utf-8")
    issues = reg.validate_project("Demo", config_root=root / "configs")
    assert any("command_workdir" in i for i in issues)


def test_load_registry_with_status_command(isolated_atlas: Path) -> None:
    root = isolated_atlas
    data = json.loads((root / "configs" / "project-registry.json").read_text(encoding="utf-8"))
    data["projects"][0]["status_command"] = "python -m app.cli doctor --full"
    data["projects"][0]["command_workdir"] = str(root / "assistant-core")
    (root / "configs" / "project-registry.json").write_text(json.dumps(data) + "\n", encoding="utf-8")
    model = load_project_registry(root / "configs")
    p = model.projects[0]
    assert p.status_command.startswith("python")
    assert str(p.command_workdir).endswith("assistant-core")
