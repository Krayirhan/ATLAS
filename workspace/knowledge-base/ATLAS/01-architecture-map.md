# ATLAS — Architecture map

| Area | Path / component | Role |
|------|------------------|------|
| Monorepo root | `E:\ATLAS` | Configs, templates, MCP helper scripts, workspace |
| CLI / Python package | `E:\ATLAS\assistant-core` | Typer CLI (`python -m app.cli`), loaders, commands |
| Configs | `E:\ATLAS\configs` | `assistant.settings.json`, `project-registry.json`, `safety-policy.json`, `mcp.master.json`, `generated/*` |
| Workspace | `E:\ATLAS\workspace` | Knowledge bases, memory DB, outputs, notebooklm exports (MCP filesystem scope) |
| MCP helpers | `E:\ATLAS\mcp-servers/*` | Local helper scripts (not full hosted MCP products) |
| Logs | `E:\ATLAS\logs` | JSONL audit streams (`tool-calls`, `sessions`, `errors`) |

**Data flow:** Registry → memory sync → context build reads knowledge + memory; reports read configs + integrations; MCP `generate` renders IDE configs from `mcp.master.json`.
