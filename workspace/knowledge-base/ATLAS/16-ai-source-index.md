# AI Source Index

## Allowed sources

| Source | Path / mechanism |
|--------|------------------|
| Project registry | `configs/project-registry.json` |
| Knowledge base (ATLAS) | `workspace/knowledge-base/ATLAS/*.md` (incl. 08–16) |
| Reports | `workspace/outputs/reports/ATLAS/*.md` |
| Memory summary | SQLite via **memory repository** APIs (project row, decisions), not arbitrary SQL strings in prompts |
| Generated report summaries | Small excerpts from latest report files only |

## Restricted sources (only with explicit user path + allow-list check)

| Source | Rule |
|--------|------|
| `assistant-core` source | Only files **explicitly listed** by the user and under `E:\ATLAS\assistant-core`, capped in size. |
| Logs | **Metadata or scrubbed** lines only; no bulk JSONL dump into prompts. |

## Blocked sources

| Source | Reason |
|--------|--------|
| `.env`, `*.pem`, keys, keystores | Secrets |
| `D:\ATLAS` | Non-canonical / policy |
| `C:\Users` full scan | Privacy |
| Browser profiles | Privacy |
| Raw `workspace/memory/assistant.db` bytes | Use repository layer instead |
| NotebookLM live API | Not in scope; file-based exports only |

## Change control

Any new source requires an update to this file + `11-ai-context-contract.md` + security review note in `15-ai-security-boundaries.md`.
