"""SQLite repositories for memory commands."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.loader import load_project_registry
from app.memory.db import AnalysisReportORM, DecisionORM, ProjectMemoryORM, ProjectORM, ToolCallORM, make_session


def sync_projects_from_registry(db_path: Path) -> tuple[int, int]:
    SessionLocal = make_session(db_path)
    reg = load_project_registry()
    added = 0
    updated = 0
    with SessionLocal() as session:
        session: Session
        for p in reg.projects:
            row = session.scalars(select(ProjectORM).where(ProjectORM.name == p.name)).first()
            if row:
                row.type = p.type
                row.root = str(p.root.resolve())
                row.knowledge = str(p.knowledge) if p.knowledge else ""
                row.updated_at = datetime.utcnow()
                updated += 1
            else:
                session.add(
                    ProjectORM(
                        name=p.name,
                        type=p.type,
                        root=str(p.root.resolve()),
                        knowledge=str(p.knowledge) if p.knowledge else "",
                    )
                )
                added += 1
        session.commit()
    return added, updated


def add_decision(db_path: Path, project_name: str, title: str, body: str) -> None:
    SessionLocal = make_session(db_path)
    with SessionLocal() as session:
        proj = session.scalars(select(ProjectORM).where(ProjectORM.name == project_name)).first()
        if not proj:
            raise ValueError(f"Unknown project in memory DB: {project_name}")
        session.add(DecisionORM(project_id=proj.id, title=title, body=body))
        session.commit()


def list_decisions(db_path: Path, project_name: str) -> list[tuple[str, str]]:
    SessionLocal = make_session(db_path)
    with SessionLocal() as session:
        proj = session.scalars(select(ProjectORM).where(ProjectORM.name == project_name)).first()
        if not proj:
            return []
        rows = session.scalars(select(DecisionORM).where(DecisionORM.project_id == proj.id)).all()
        return [(r.title, r.body) for r in rows]


def set_project_status(db_path: Path, project_name: str, status: str) -> None:
    SessionLocal = make_session(db_path)
    with SessionLocal() as session:
        proj = session.scalars(select(ProjectORM).where(ProjectORM.name == project_name)).first()
        if not proj:
            raise ValueError(f"Unknown project: {project_name}")
        row = session.scalars(
            select(ProjectMemoryORM).where(
                ProjectMemoryORM.project_id == proj.id,
                ProjectMemoryORM.key == "status",
            )
        ).first()
        if row:
            row.value = status
            row.updated_at = datetime.utcnow()
        else:
            session.add(ProjectMemoryORM(project_id=proj.id, key="status", value=status))
        session.commit()


def get_project_status(db_path: Path, project_name: str) -> str:
    SessionLocal = make_session(db_path)
    with SessionLocal() as session:
        proj = session.scalars(select(ProjectORM).where(ProjectORM.name == project_name)).first()
        if not proj:
            return "not in database (run memory sync-projects)"
        row = session.scalars(
            select(ProjectMemoryORM).where(
                ProjectMemoryORM.project_id == proj.id,
                ProjectMemoryORM.key == "status",
            )
        ).first()
        return row.value if row else "(no status set)"


def log_tool_call(db_path: Path, project_name: str, command: str, mode: str, result: str) -> None:
    SessionLocal = make_session(db_path)
    with SessionLocal() as session:
        session.add(
            ToolCallORM(
                project_name=project_name,
                command=command,
                mode=mode,
                result=(result or "")[:8000],
            )
        )
        session.commit()


def add_analysis_report(db_path: Path, project_name: str, report_type: str, path: str) -> None:
    SessionLocal = make_session(db_path)
    with SessionLocal() as session:
        proj = session.scalars(select(ProjectORM).where(ProjectORM.name == project_name)).first()
        if not proj:
            raise ValueError(f"Unknown project in memory DB: {project_name}")
        session.add(AnalysisReportORM(project_id=proj.id, report_type=report_type, path=str(path)))
        session.commit()


def list_analysis_reports(db_path: Path, project_name: str) -> list[tuple[str, str, datetime]]:
    SessionLocal = make_session(db_path)
    with SessionLocal() as session:
        proj = session.scalars(select(ProjectORM).where(ProjectORM.name == project_name)).first()
        if not proj:
            return []
        rows = session.scalars(
            select(AnalysisReportORM)
            .where(AnalysisReportORM.project_id == proj.id)
            .order_by(AnalysisReportORM.id.desc())
        ).all()
        return [(r.report_type, r.path, r.created_at) for r in rows]


def latest_analysis_report(db_path: Path, project_name: str) -> tuple[str, str, datetime] | None:
    rows = list_analysis_reports(db_path, project_name)
    return rows[0] if rows else None
