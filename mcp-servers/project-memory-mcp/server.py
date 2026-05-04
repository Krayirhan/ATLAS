"""Read-only project-memory server (Sprint 16 foundation).

This V1 implementation provides read-only commands and intentionally avoids any
write/update operations.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


def _atlas_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _registry_path() -> Path:
    return _atlas_root() / "configs" / "project-registry.json"


def _memory_db_path() -> Path:
    return _atlas_root() / "workspace" / "memory" / "assistant.db"


def read_project_registry() -> dict:
    return json.loads(_registry_path().read_text(encoding="utf-8-sig"))


def _project(project_name: str) -> dict | None:
    reg = read_project_registry()
    return next((p for p in reg.get("projects", []) if p.get("name") == project_name), None)


def read_project_summary(project_name: str) -> dict:
    project = _project(project_name)
    if not project:
        raise ValueError(f"Unknown project: {project_name}")
    knowledge = project.get("knowledge") or str(_atlas_root() / "workspace" / "knowledge-base" / project_name)
    summary = Path(knowledge) / "00-project-summary.md"
    if not summary.exists():
        return {"project": project_name, "summary_path": str(summary), "summary": ""}
    return {"project": project_name, "summary_path": str(summary), "summary": summary.read_text(encoding="utf-8")}


def read_project_status(project_name: str) -> dict:
    db = _memory_db_path()
    if not db.exists():
        return {"project": project_name, "status": "", "note": "memory db does not exist"}
    with sqlite3.connect(str(db)) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT pm.value
            FROM project_memories pm
            JOIN projects p ON p.id = pm.project_id
            WHERE p.name = ? AND pm.key = 'status'
            ORDER BY pm.id DESC
            LIMIT 1
            """,
            (project_name,),
        )
        row = cur.fetchone()
    return {"project": project_name, "status": row[0] if row else ""}


def list_decisions(project_name: str) -> dict:
    db = _memory_db_path()
    if not db.exists():
        return {"project": project_name, "decisions": []}
    with sqlite3.connect(str(db)) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT d.title, d.body, d.created_at
            FROM decisions d
            JOIN projects p ON p.id = d.project_id
            WHERE p.name = ?
            ORDER BY d.id DESC
            """,
            (project_name,),
        )
        rows = cur.fetchall()
    return {
        "project": project_name,
        "decisions": [{"title": r[0], "body": r[1], "created_at": r[2]} for r in rows],
    }


def list_reports(project_name: str) -> dict:
    db = _memory_db_path()
    if not db.exists():
        return {"project": project_name, "reports": []}
    with sqlite3.connect(str(db)) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.report_type, a.path, a.created_at
            FROM analysis_reports a
            JOIN projects p ON p.id = a.project_id
            WHERE p.name = ?
            ORDER BY a.id DESC
            """,
            (project_name,),
        )
        rows = cur.fetchall()
    return {
        "project": project_name,
        "reports": [{"report_type": r[0], "path": r[1], "created_at": r[2]} for r in rows],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ATLAS project-memory read-only server")
    parser.add_argument(
        "action",
        choices=[
            "read_project_registry",
            "read_project_summary",
            "read_project_status",
            "list_decisions",
            "list_reports",
        ],
    )
    parser.add_argument("--project", help="Project name for project-scoped actions")
    args = parser.parse_args()
    action = args.action
    project = args.project
    if action == "read_project_registry":
        result = read_project_registry()
    elif action == "read_project_summary":
        if not project:
            raise SystemExit("--project is required")
        result = read_project_summary(project)
    elif action == "read_project_status":
        if not project:
            raise SystemExit("--project is required")
        result = read_project_status(project)
    elif action == "list_decisions":
        if not project:
            raise SystemExit("--project is required")
        result = list_decisions(project)
    else:
        if not project:
            raise SystemExit("--project is required")
        result = list_reports(project)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
