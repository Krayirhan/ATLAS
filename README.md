# ATLAS AI Assistant

## What is ATLAS?

ATLAS is a local-first, security-first developer AI control plane. It centralizes project memory, instruction surfaces, JSON configs, safety policy, logs, reports, and bounded AI agent workflows so humans and AI operate under the same guardrails.

## Current status

| Item | Value |
|------|--------|
| Release | V1 RC - GO |
| Root | `E:\ATLAS` |
| Self-project | `ATLAS` |
| `D:\ATLAS` | Not used as operational root |
| Tests | Run `python -m pytest -q` from `assistant-core` |
| Health | `python -m app.cli doctor --full` |
| Audit | `python -m app.cli audit v1-rc` |

## Security model

- No full-disk MCP
- No secret file reading in product scope
- No `D:` writes as ATLAS policy stance
- Command preview never executes
- No git push / production deploy automation
- No autonomous coding agent execution path

## Forward-looking sprint map

- Sprint 28: Ollama AI layer foundation
- Sprint 29: MemoryAgent / ProjectQAAgent
- Sprint 30: PlannerAgent
- Sprint 31: CodeReviewerAgent
- Sprint 32: ToolApproval design
- Sprint 33: MainAgent alpha
- Sprint 34: SecurityAuditorAgent
- Sprint 35: DocumentationAgent

## SecurityAuditorAgent

- `python -m app.cli ai security-audit --project ATLAS --provider mock --scope all-light`
- `python -m app.cli ai security-audit --project ATLAS --provider mock --scope agents --show-sources`
- `python -m app.cli ai security-audit --project ATLAS --provider mock --scope mcp`
- `python -m app.cli ai main --project ATLAS --provider mock --show-routing "ATLAS guvenli mi?"`

SecurityAuditorAgent read-only calisir. Dosya degistirmez, terminal calistirmaz, Git/MCP tool cagrisi yapmaz. Agent capability, MCP exposure, approval policy, context source ve secret-risk sinirlarini denetler.

## DocumentationAgent

Sprint 35 ile `DocumentationAgent` geldi. Read-only dokümantasyon audit'i üretir.
README, KB, NotebookLM workflow, roadmap, agent sprint dokümanları ve release dokümanlarını kontrol eder.
Dosya değiştirmez. Terminal çalıştırmaz. Git/MCP tool çağırmaz.

```powershell
python -m app.cli ai docs-audit --project ATLAS --provider mock --scope all-light
python -m app.cli ai docs-audit --project ATLAS --provider mock --scope notebooklm --show-sources
python -m app.cli ai docs-audit --project ATLAS --provider mock --scope agents
python -m app.cli ai main --project ATLAS --provider mock --show-routing "README guncel mi?"
```

## Repo

https://github.com/Krayirhan/ATLAS
