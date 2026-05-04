# AI Security Boundaries

## Read-only AI boundary

The AI layer **never** writes to disk, never runs shell commands, and never invokes MCP or other tools as part of model completion in Sprint 28–29 baseline.

## Prohibited capabilities

| Boundary | Rule |
|----------|------|
| File write | No create/overwrite/delete via AI commands. |
| Terminal run | No subprocess from `ai` CLI. |
| Tool call | No MCP / function-calling from model output execution path. |
| Secret read | No `.env`, keys, keystores, browser profiles in context. |
| Full disk scan | No unconstrained filesystem walks. |
| MCP run | AI must not start MCP servers. |
| `D:\ATLAS` | Not an operational root; not a context source. |
| `C:\Users` crawl | No “read all of Users” patterns. |

## Audit logging policy

- **Allowed:** metadata events (`ai_ask_started`, `project`, `model`, `duration_ms`, success/fail) without raw prompts if policy tightens later.
- **Avoid:** full prompt/response logging in shared logs (secret leakage risk). Prefer **opt-in** local debug files under `workspace/outputs` for developers only, never committed.

## Allowed read sources (summary)

See full list in `16-ai-source-index.md`: registry, KB ATLAS markdown, reports, memory via repository.

## Blocked sources (summary)

Secrets, keys, `D:\ATLAS`, unconstrained Users tree, raw log bodies with possible tokens.

## Future: approval workflow

Later sprints may introduce **explicit human approval** before any non-read-only action. Until then, **no** such actions from AI paths.
