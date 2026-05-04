"""Non-collected helpers for registry fixtures."""

from __future__ import annotations

import json
from pathlib import Path


def write_atlas_only_registry(root: Path) -> None:
    kb = root / "workspace" / "knowledge-base" / "ATLAS"
    kb.mkdir(parents=True, exist_ok=True)
    (kb / "00-project-summary.md").write_text("# s\n", encoding="utf-8")
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
