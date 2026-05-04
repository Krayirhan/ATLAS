# ATLAS — Feature index (V1 skeleton)

- **paths** — Resolve ATLAS root and standard directories.
- **config validate** — Validate settings, registry, safety, MCP master (+ workspace-filesystem path rules).
- **safety show** — Summarize policy.
- **project** — List / show / validate / add projects.
- **mcp** — List servers, `generate` (optional `--dry-run`), conservative `install`.
- **memory** — SQLite init, sync from registry, decisions, project status.
- **context** — Build context plan from knowledge + memory metadata.
- **command** — `check` / `preview` with safety guard (no execution in preview).
- **logs** — `list`, `show`, `project <name> [--last]` (read-only, resilient JSONL).
- **report** — Create typed markdown reports under `workspace/outputs/reports/<project>/`.
- **doctor** / **doctor --full** — Layout + config + optional toolchain probes.
- **audit v1-rc** — Static RC checklist markdown.
- **integrations** — Instruction file presence (with monorepo `assistant-core` root when applicable).
