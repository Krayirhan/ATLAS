# ATLAS — Risk list

1. **`D:` volume / `D:\ATLAS` confusion** — Operational work must stay on **`E:\ATLAS`**; stale docs or shortcuts referencing `D:\ATLAS` create misconfiguration risk.
2. **MCP helpers vs real servers** — Bundled scripts may not implement full MCP stdio semantics; treat as local helpers only.
3. **Safe-terminal** — Any future “real run” must remain gated; V1 stays preview-first.
4. **Context budgets** — Token fields are **planned**, not exact LLM meter readings.
5. **Report / audit depth** — Improved in Sprint 27; still not a substitute for human release review.
6. **Nested automation** — Report generation can probe `doctor`/`pytest`; CI may set `ATLAS_REPORT_LIGHT=1` to skip nested subprocesses.
7. **V2+ scope creep** — Agents, routers, RAG, and desktop UI remain **explicitly out of V1**.
