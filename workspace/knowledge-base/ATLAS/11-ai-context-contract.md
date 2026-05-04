# AI Context Contract

This document defines **which sources** are assembled for the AI and in **what order**, before any Sprint 28 `ai ask` implementation.

## Read order (default stack)

1. `configs/project-registry.json` (project entry for the named project, e.g. ATLAS).
2. **SQLite memory** — project status / decisions via the **memory repository** abstraction (not ad-hoc raw DB dumps in prompts).
3. `workspace/knowledge-base/ATLAS/00-project-summary.md`
4. `workspace/knowledge-base/ATLAS/03-current-status.md`
5. `workspace/knowledge-base/ATLAS/04-risk-list.md`
6. `workspace/knowledge-base/ATLAS/05-release-checklist.md`
7. `workspace/knowledge-base/ATLAS/06-next-sprints.md`
8. `workspace/knowledge-base/ATLAS/07-v1-rc-go-report.md`
9. **Latest reports** — small set from `workspace/outputs/reports/<project>/` (newest first, capped).
10. **User-attached path** — only when the user explicitly names an allowed file under ATLAS (see `16-ai-source-index.md`).

## Forbidden sources (must never enter model context)

- `.env` and any env file containing secrets  
- Private keys, SSH keys, keystores, browser profiles  
- **`C:\Users` as a whole-disk crawl**  
- **`D:\ATLAS`** and `D:` operational experiments (policy: unhealthy / non-canonical)  
- Full-repository source scans  
- Raw logs that may contain tokens — use **metadata or scrubbed** views only  

## Context package shape (logical schema)

The assembler should produce a structured object (conceptual; Sprint 28 may use Pydantic or dict):

| Field | Content |
|-------|---------|
| `project_identity` | Name, type, root, knowledge path, workdir |
| `current_status` | Summary + 03-current-status excerpts |
| `risks` | 04-risk-list excerpts |
| `next_sprints` | 06-next-sprints excerpts |
| `recent_reports` | Short excerpts or titles + paths |
| `user_question` | Verbatim user ask |
| `safety_rules` | Short list: read-only, no terminal, no file write, blocked paths |

## Task types (for routing / budget)

| Task | Notes |
|------|--------|
| `project_status` | Medium context; registry + memory + summary + status. |
| `sprint_plan` | Medium–high; include 06-next-sprints + risks. |
| `risk_review` | Emphasize 04 + reports tagged risk/audit. |
| `ai_readiness` | Checklist against 07 + 13 + 15. |
| `release_audit` | High; still file-bounded, no repo-wide scan. |
| `code_review_readonly` | High; **only** explicitly listed files under allowed roots. |

## Token budget (heuristic)

| Class | Budget |
|-------|--------|
| Simple question | Low |
| Project status | Medium |
| Sprint plan | Medium–high |
| Code review (readonly) | High but **strict file list** |

**Note:** Budgets are **planned**, not exact token counts from providers (see V1 context builder notes).

## Alignment

- Matches the spirit of `app/context/builder.py` read/skip lists; Sprint 28 AI assembler should **not** contradict this contract without a documented change here.
