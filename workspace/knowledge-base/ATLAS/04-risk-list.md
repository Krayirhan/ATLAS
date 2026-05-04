# ATLAS — Risk list

1. **D: volume health** — `D:` is treated as unhealthy; avoid reads/writes there; stale `D:\ATLAS` references in old docs or caches are a confusion risk.
2. **MCP helper scripts** — Bundled `project-memory-mcp` / `safe-terminal-mcp` are not guaranteed to implement full stdio MCP protocol; treat as local helpers only.
3. **Safe-terminal** — Any future “real run” path must stay behind explicit approvals; V1 stays preview-first.
4. **Context manager** — Token estimates may be heuristic, not exact provider token counts.
5. **Reports** — Many report types are structured outlines; depth hardening is ongoing (V1.1+).
6. **Test coverage** — Core paths are covered; expand as features grow.
7. **V2 agent orchestrator** — Explicitly out of V1 scope (separate program increment).
