# ATLAS AI Assistant

## What is ATLAS?

ATLAS is a **local-first**, **security-first**, and **token-aware** personal **developer AI control plane** for Windows (and paths are portable). It is **not a chatbot**: it centralizes **project memory** (SQLite), **instruction surfaces** (AGENTS / Copilot / Cursor / Codex templates), **JSON configs**, **safety policy**, **structured logs**, **markdown reports**, and **MCP config generation** so AI tools and humans share the same guardrails.

## Current status

| Item | Value |
|------|--------|
| **Release** | **V1 RC — GO** |
| **Root** | `E:\ATLAS` (canonical monorepo root) |
| **Self-project** | **ATLAS** (`python-cli`, see `configs/project-registry.json`) |
| **BenimFormum** | **Not** the current pilot (do not treat as a V1 requirement) |
| **`D:\ATLAS`** | **Not** used as an operational root; avoid `D:` writes in ATLAS workflows |
| **RC record** | `workspace/knowledge-base/ATLAS/07-v1-rc-go-report.md` |
| **Tests** | Run `python -m pytest -q` from `assistant-core` for the latest count |
| **Health** | `python -m app.cli doctor` / `doctor --full` |
| **Audit** | `python -m app.cli audit v1-rc` |

## Core capabilities

- Python **CLI** (`assistant-core`, Typer)
- **Config validation** (`config validate`)
- **Safety policy** (blocked paths/patterns/commands, approval hints)
- **Project registry** (typed projects, commands, forbidden-change strings)
- **Instruction generator** (templates → repo files)
- **MCP config generator** (`mcp generate`, optional `--dry-run`)
- **SQLite memory** (`memory init`, `sync-projects`, decisions)
- **NotebookLM** manual import pipeline (file-based, no cloud API in V1)
- **Context manager** (read plans / token **budgets** — estimates, not measured LLM tokens)
- **Command check / preview** (preview **never** executes the shell command)
- **Audit logs** (JSONL, `logs project` filters)
- **Report generator** (typed markdown under `workspace/outputs/reports/…`)
- **Doctor** / **doctor --full**
- **V1 RC audit** (`audit v1-rc`)

## Security model

- **No full-disk MCP** — `workspace-filesystem` is validated to match `E:\ATLAS\workspace` (see `config validate`).
- **No secret file reading** in product scope; do not commit `.env`, keys, keystores, or browser profiles.
- **`D:\ATLAS`** is not an operational root; **no writes to `D:`** as an ATLAS policy stance.
- **`command preview`** does **not** run commands; it resolves registry + policy only.
- **`safe-terminal`** real execution is **not** expanded in V1.
- **No git push / production deploy automation** in this repo.
- **No autonomous coding agent** in V1.

## Folder structure

```text
E:\ATLAS
├── assistant-core/     # Python package + CLI entrypoint
├── workspace/          # knowledge-base, memory DB, outputs, exports
├── configs/            # JSON + generated MCP IDE configs
├── templates/          # Jinja instruction templates
├── logs/               # JSONL streams (tool-calls, sessions, errors)
├── backups/            # reserved for local backups
└── mcp-servers/        # local helper scripts (not full hosted MCP products)
```

## Installation / local usage (PowerShell)

```powershell
cd E:\ATLAS\assistant-core
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"   # if dev extra exists; else pip install -e .
python -m pytest -q
python -m app.cli doctor
python -m app.cli doctor --full
python -m app.cli config validate
```

## Main CLI commands

| Command | Purpose |
|---------|---------|
| `python -m app.cli doctor` | Quick layout + config + safety |
| `python -m app.cli doctor --full` | Extended checks (optional tools may warn) |
| `python -m app.cli paths` | Print canonical paths |
| `python -m app.cli config validate` | Validate all JSON configs + MCP workspace rule |
| `python -m app.cli safety show` | Summarize policy |
| `python -m app.cli project list` | Registry listing |
| `python -m app.cli project validate ATLAS` | Validate ATLAS paths |
| `python -m app.cli mcp list` | MCP server keys from master file |
| `python -m app.cli mcp generate --target all --dry-run` | Preview generated MCP files (no write) |
| `python -m app.cli memory sync-projects` | Sync registry → SQLite |
| `python -m app.cli context build ATLAS --task project_status` | JSON read plan |
| `python -m app.cli command check ATLAS --cmd "..."` | Policy evaluation |
| `python -m app.cli command preview ATLAS --type test` | Resolved test command (no run) |
| `python -m app.cli logs list` | Log streams overview |
| `python -m app.cli logs project ATLAS --last 10` | Filter JSONL by project |
| `python -m app.cli report create ATLAS --type system-health` | Markdown system report |
| `python -m app.cli audit v1-rc` | RC checklist + verdict |

## Reports & audit

- `python -m app.cli report create ATLAS --type system-health`
- `python -m app.cli report create ATLAS --type integration-check`
- `python -m app.cli report list ATLAS` / `report latest ATLAS`
- `python -m app.cli audit v1-rc` — writes under `workspace/outputs/reports/V1/`
- Re-run **`doctor --full`** after layout or toolchain changes.

**CI / nested tests:** set `ATLAS_REPORT_LIGHT=1` so report generation skips nested `doctor`/`pytest` subprocess probes (avoids recursion in automated test runs).

## V1 / V1.1 / V2 / V3 roadmap

| Track | Scope |
|-------|--------|
| **V1** | Control plane: safety, registry, memory, reports, doctor, MCP config generation |
| **V1.1** | Test/report depth, MCP protocol prep, polish — **no** LLM product |
| **V2** | AI layer: LLM providers, read-only `ai ask`, MemoryAgent, PlannerAgent, CodeReviewerAgent |
| **V3** | Desktop UI, chat panel, tool-approval UX, token usage dashboards |

### Forward-looking sprint map (documentation only)

- **Sprints 25–27:** V1 stabilization (docs, tests, reports) — **no AI runtime**.
- **Sprint 28:** AI Layer Foundation (interfaces, prompt composer, read-only ask).
- **Sprint 29:** MemoryAgent / ProjectQAAgent.
- **Sprint 30:** PlannerAgent.
- **Sprint 31:** CodeReviewerAgent.
- **Sprint 32:** Tool approval design.
- **Sprint 33:** MainAgent alpha.

## Not included in V1

- Autonomous coding agent / model router
- OpenAI / Ollama adapters
- RAG / vector index service
- Desktop UI
- Production deploy or git-push automation
- Full MCP stdio protocol compliance for helper scripts (helpers remain local)

## GitHub / portfolio notes

Position ATLAS as an **engineering control plane**: you own configs, policy, and evidence (logs + reports), not a black-box assistant. Mention **GO** RC, explicit **out-of-scope** list, and that **preview** paths are safe-by-design for reviews and hiring conversations.

**Repo:** https://github.com/Krayirhan/ATLAS
