# ATLAS — Risk list

1. **`D:` volume / `D:\ATLAS` confusion** — Operational work must stay on **`E:\ATLAS`**; stale docs or shortcuts referencing `D:\ATLAS` create misconfiguration risk.
2. **MCP helpers vs real servers** — Bundled scripts may not implement full MCP stdio semantics; treat as local helpers only.
3. **Safe-terminal** — Any future “real run” must remain gated; V1 stays preview-first.
4. **Context budgets** — Token fields are **planned**, not exact LLM meter readings.
5. **Report / audit depth** — Improved in Sprint 27; still not a substitute for human release review.
6. **Nested automation** — Report generation can probe `doctor`/`pytest`; CI may set `ATLAS_REPORT_LIGHT=1` to skip nested subprocesses.
7. **V2+ scope creep** — Agents, routers, RAG, and desktop UI remain **explicitly out of V1**.
8. **AI hallucination** — Model answers may invent facts if context is thin; mitigated by read-only mode, source citations, and “insufficient context” policy (`12-ai-prompt-policy.md`).
9. **Stale knowledge-base** — KB not refreshed after sprints leads to wrong “current status”; mitigated by reports + NotebookLM import discipline (`10-notebooklm-workflow.md`).
10. **NotebookLM summary quality** — Manual summaries can be wrong or incomplete; treat as advisory; validate against registry and reports.
11. **Ollama model availability** — Model not pulled, Ollama stopped, or wrong tag breaks `ai doctor` / `ai ask` once implemented (`09-ollama-integration-plan.md`).
12. **Prompt context overload** — Too much text in one prompt risks truncation, cost, and confusion; follow token budgets in `11-ai-context-contract.md`.
13. **Secret leakage via AI path** — If future code ever fed secrets or raw logs into prompts; blocked by `15-ai-security-boundaries.md` and `16-ai-source-index.md`.
