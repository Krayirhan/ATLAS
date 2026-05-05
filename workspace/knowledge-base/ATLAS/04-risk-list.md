# ATLAS - Risk list

1. **`D:` volume / `D:\ATLAS` confusion** - Operational work must stay on `E:\ATLAS`.
2. **MCP helpers vs real servers** - Bundled scripts are local helpers, not unrestricted servers.
3. **Safe-terminal** - Any future real run path must remain gated.
4. **Context budgets** - Prompt size is bounded but still requires review as scope grows.
5. **Report / audit depth** - Helpful evidence, not a substitute for human release review.
6. **Nested automation** - CI may need `ATLAS_REPORT_LIGHT=1` to avoid nested probes.
7. **V2+ scope creep** - Agents, routers, RAG, and desktop UI remain outside V1 baseline.
8. **AI hallucination** - Responses can drift if context is thin; mitigated by read-only mode and source-aware policy.
9. **Stale knowledge-base** - KB drift can degrade current-status quality.
10. **NotebookLM summary quality** - Manual summaries remain advisory.
11. **Ollama model availability** - Missing or cold models can slow or block runtime answers.
12. **Prompt context overload** - Too much text risks truncation and confusion.
13. **Secret leakage via AI path** - Must stay blocked by source contract and safety boundaries.
14. **Security audit drift** - Capability flags, MCP bounds, approval policy, or context contract can diverge without regression checks.
