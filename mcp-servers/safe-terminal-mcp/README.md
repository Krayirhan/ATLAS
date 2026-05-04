# safe-terminal-mcp (Sprint 17)

V1 helper script (non-stdio MCP): registry-backed commands only.

## Actions

- `check` — resolve command + safety evaluation (no execution)
- `preview` — same as `check` (no execution)
- `run` — requires `ATLAS_SAFE_TERMINAL_APPROVAL_TOKEN` env to match `--approval-token`

## Project selection

- `--project Name` or env `ATLAS_SAFE_TERMINAL_PROJECT`
- If registry has exactly one project, that name is used as default

## Examples

```powershell
$env:ATLAS_ROOT="E:\ATLAS"
python server.py preview --project AtlasOnboard --type status
$env:ATLAS_SAFE_TERMINAL_APPROVAL_TOKEN="demo-token"
python server.py run --project AtlasOnboard --type status --approval-token demo-token
```

## Safety

- Blocked commands from `configs/safety-policy.json` are rejected
- Shell metacharacters (`;|&` newline backtick) are rejected for `run`
- Working directory is the project `root` from registry
