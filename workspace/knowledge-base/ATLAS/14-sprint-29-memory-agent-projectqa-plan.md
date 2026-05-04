# Sprint 29 — MemoryAgent + ProjectQAAgent Alpha

## Purpose

Add two **thin, read-only** helpers that sit on the Sprint 28 AI foundation:

- **MemoryAgent** — answers questions about **SQLite memory** content (project status, decisions) using repository APIs, not raw SQL in prompts.
- **ProjectQAAgent** — answers **project definition** questions (registry, knowledge-base headings, recent reports) with citations to paths/sections.

## What they are not

- **Not** autonomous coding agents.  
- **Not** planners or patch appliers.  
- **Not** tool runners or terminal executors.

They remain **read-only** and return **natural language** (and optional structured JSON for CLI display).

## Relationship to context loader

Both agents use the **same context contract** (`11-ai-context-contract.md`) and **source index** (`16-ai-source-index.md`). They specialize **which slices** get higher weight in the prompt (memory vs KB vs reports).

## Sources

- Registry + memory repository summaries + KB markdown + curated report excerpts — same allowed set as Sprint 28.

## CLI examples (planned — Sprint 29)

```text
python -m app.cli ai ask --project ATLAS "Son kararlar neler?"
python -m app.cli ai status --project ATLAS
```

*(Exact flags subject to Sprint 29 UX pass; may map to agent mode behind `--mode`.)*

## Out of scope

- Terminal, file write, git, MCP tool calls.
- Planner loops and code patch application.
- Multi-step autonomous workflows.

## Exit criteria (alpha)

- Documented behavior + tests for memory-only and KB-only questions.
- Fails closed when question would require blocked sources.
