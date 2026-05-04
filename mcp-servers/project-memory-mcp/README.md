# project-memory-mcp (Sprint 16)

Read-only project intelligence adapter for:

- `configs/project-registry.json`
- `workspace/knowledge-base/*`
- `workspace/memory/assistant.db`

Supported read actions:

- `read_project_registry`
- `read_project_summary`
- `read_project_status`
- `list_decisions`
- `list_reports`

Example:

```powershell
python server.py read_project_registry
python server.py read_project_summary --project AtlasOnboard
python server.py read_project_status --project AtlasOnboard
```

Security:

- no write/update/delete operations
- no terminal command execution
