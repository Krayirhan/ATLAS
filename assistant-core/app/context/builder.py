"""Build token-aware context read plans (Sprint 10)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from app.config.loader import load_project_registry
from app.paths import get_memory_db_path, get_workspace_dir


TASK_ALIASES = {
    "project_status": "project_status",
    "project-status": "project_status",
    "sprint_plan": "sprint_plan",
    "sprint-plan": "sprint_plan",
    "code_review": "code_review",
    "code-review": "code_review",
    "simple_question": "simple_question",
    "simple-question": "simple_question",
    "release_audit": "release_audit",
    "release-audit": "release_audit",
    "large_audit": "large_audit",
    "integration_check": "integration_check",
    "integration-check": "integration_check",
}

# Sprint 21: optional high-signal roots relative to project root (read if present).
TYPE_EXTRA_HINT_FILES: dict[str, list[str]] = {
    "android-compose-room": ["settings.gradle.kts", "settings.gradle", "build.gradle.kts", "build.gradle"],
    "android-compose-notes": ["settings.gradle.kts", "settings.gradle", "build.gradle.kts", "build.gradle"],
    "mlops-python": ["pyproject.toml", "requirements.txt", "environment.yml", "README.md"],
    "spring-boot": ["pom.xml", "build.gradle", "build.gradle.kts", "README.md"],
    "unity-game": ["ProjectSettings/ProjectVersion.txt", "Packages/manifest.json", "README.md"],
    "plain-java": ["pom.xml", "build.gradle", "README.md"],
    "python-cli": ["pyproject.toml", "README.md"],
}

TOKEN_BUDGET = {
    "simple_question": 4000,
    "project_status": 8000,
    "sprint_plan": 12000,
    "code_review": 25000,
    "release_audit": 60000,
    "large_audit": 60000,
    "integration_check": 8000,
}


@dataclass
class ContextPlan:
    task: str
    project_name: str
    token_budget: int
    read: List[str] = field(default_factory=list)
    skip: List[str] = field(default_factory=list)
    rationale: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    planned_read_order: List[str] = field(default_factory=list)
    token_budget_note: str = ""
    ai_layer_note: str = ""


def normalize_task(task: str) -> str:
    key = task.strip().lower().replace(" ", "_")
    return TASK_ALIASES.get(key, key)


def build_plan(project_name: str, task: str) -> ContextPlan:
    t = normalize_task(task)
    budget = TOKEN_BUDGET.get(t, 8000)
    reg = load_project_registry()
    proj = next((p for p in reg.projects if p.name == project_name), None)
    if not proj:
        return ContextPlan(
            task=t,
            project_name=project_name,
            token_budget=budget,
            risks=[f"Unknown project: {project_name}"],
            token_budget_note="Token budget is planned only (no LLM calls in V1).",
            ai_layer_note="Resolve registry entry before Sprint 28 AI work.",
        )

    ws = get_workspace_dir()
    kb = Path(str(proj.knowledge)) if proj.knowledge else ws / "knowledge-base" / project_name
    summary = kb / "00-project-summary.md"
    mem_db = get_memory_db_path()

    read: List[str] = []
    skip: List[str] = []
    rationale: List[str] = []
    risks: List[str] = []

    read.append(f"project-registry entry for {project_name}")
    rationale.append("Registry is the smallest authoritative project config.")

    if mem_db.is_file():
        read.append(f"SQLite memory ({mem_db.name}) — project row + status/decisions")
        rationale.append("Structured status beats scanning the repo for simple questions.")
    else:
        skip.append(str(mem_db))
        rationale.append("Memory DB not initialized yet; run `memory init`.")

    if summary.is_file():
        read.append(str(summary))
        rationale.append("Summary-first per ATLAS token policy.")
    else:
        risks.append(f"Missing {summary}; context will be thinner.")

    for rel in TYPE_EXTRA_HINT_FILES.get(proj.type, []):
        if ".." in Path(rel).parts:
            continue
        hint = (proj.root / rel).resolve()
        try:
            hint.relative_to(proj.root.resolve())
        except ValueError:
            continue
        if hint.is_file():
            read.append(str(hint))
    if TYPE_EXTRA_HINT_FILES.get(proj.type):
        rationale.append(f"Type-specific hints for `{proj.type}` (only files that exist).")

    wide_tasks = {"code_review", "release_audit", "large_audit", "sprint_plan"}
    if t in wide_tasks:
        for name in (
            "01-architecture-map.md",
            "02-feature-index.md",
            "03-current-status.md",
            "04-risk-list.md",
        ):
            p = kb / name
            if p.is_file():
                read.append(str(p))
        rationale.append("Wider task: include architecture, features, status, risks.")
    else:
        for name in ("01-architecture-map.md", "02-feature-index.md", "03-current-status.md"):
            skip.append(str(kb / name))
        rationale.append("Narrow task: defer deep architecture files unless explicitly needed.")

    outputs = ws / "outputs"
    if outputs.is_dir():
        read.append(str(outputs / "... latest reports only (manual pick)"))
        rationale.append("Recent reports before touching raw source.")
    else:
        skip.append(str(outputs))

    read.append("(optional) targeted source files under project root - only after summaries")
    rationale.append("Never load the full repo into context for simple_question / project_status.")

    if t == "simple_question":
        skip.append(str(proj.root / "… entire project tree"))
        risks.append("If answers need code, escalate task type to code_review.")

    planned_read_order = [
        "1. Project registry entry (authoritative name, paths, commands).",
        "2. SQLite memory (assistant.db) — project row, status, decisions (if initialized).",
        f"3. Knowledge base markdown under `{kb}` (summary first, then deeper files by task).",
        "4. Latest reports under `workspace/outputs/reports/...` (manual selection; avoid bulk).",
        "5. Targeted source files under project root only when summaries are insufficient.",
    ]
    token_budget_note = (
        "Token budget is planned/heuristic for ordering reads; ATLAS V1 does not call LLMs or count real tokens."
    )
    ai_layer_note = (
        "Sprint 28+ AI Layer is expected to consume these plans as read-only input before any `ai ask` or agents."
    )

    return ContextPlan(
        task=t,
        project_name=project_name,
        token_budget=budget,
        read=read,
        skip=skip,
        rationale=rationale,
        risks=risks,
        planned_read_order=planned_read_order,
        token_budget_note=token_budget_note,
        ai_layer_note=ai_layer_note,
    )
