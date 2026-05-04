# ATLAS AI Layer Design

## Purpose of the AI layer

The **AI layer** answers structured questions about ATLAS and the self-project using **curated context** (registry, memory, knowledge-base, reports, NotebookLM-derived summaries). It sits **above** the V1 control plane: it consumes what ATLAS already stores; it does not replace configs, safety, or doctor.

## V1 control plane vs V2 AI layer

| Aspect | V1 control plane | V2 AI layer (planned) |
|--------|------------------|------------------------|
| Role | CLI, validation, policy, MCP config, memory, reports | Optional local LLM advisory (read-first) |
| Execution | No model inference in V1 product | Inference under strict boundaries |
| Mutations | User-driven file edits, explicit commands | **No** autonomous file/terminal/git actions in early AI |

## First AI release posture: read-only

The **first** ATLAS AI surface is **read-only advisory**: answers and explanations only. No file writes, no terminal runs, no git operations, no MCP tool execution, no full-repository scans.

## Sources the AI may read (design intent)

1. **`configs/project-registry.json`** — project identity, paths, commands.
2. **SQLite memory** (`workspace/memory/assistant.db`) — via repository/summary patterns, not raw arbitrary SQL dumps in prompts.
3. **`workspace/knowledge-base/ATLAS/*.md`** — canonical narrative (summary, status, risks, sprints, RC report, AI prep docs 08–16).
4. **`workspace/outputs/reports/ATLAS/*.md`** — recent generated reports (selected, not bulk).
5. **NotebookLM-imported summaries** — after `notebooklm import` has placed structured content into the knowledge-base or linked exports (see `10-notebooklm-workflow.md`).

## What the AI must not do (baseline)

- Change files or apply patches automatically.
- Run terminal commands or suggest bypassing `command preview` / safety.
- Perform `git push`, deploy, or production actions.
- Invoke MCP servers or broaden MCP scope.
- Scan the entire repo or stream raw logs that may contain secrets.

## Sprint scope (roadmap level)

- **Sprint 28 —** AI Layer Foundation: Ollama-oriented **read-only** `ai ask` / `ai doctor` **design and minimal implementation** per `13-sprint-28-ai-layer-foundation-plan.md` (no agents).
- **Sprint 29 —** MemoryAgent + ProjectQAAgent **alpha** as read-only helpers over the same sources (`14-sprint-29-memory-agent-projectqa-plan.md`).
- **Sprint 30+ —** PlannerAgent, CodeReviewerAgent, tool approval, MainAgent — **out of scope** until prior sprints are stable; see `06-next-sprints.md` and README roadmap.

## References

- Context contract: `11-ai-context-contract.md`
- Prompt policy: `12-ai-prompt-policy.md`
- Security: `15-ai-security-boundaries.md`, `16-ai-source-index.md`
- Ollama plan: `09-ollama-integration-plan.md`
