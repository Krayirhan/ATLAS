# ATLAS — V1 RC checklist

- [ ] `python -m app.cli config validate`
- [ ] `python -m app.cli doctor`
- [ ] `python -m app.cli doctor --full` (accept optional tool warnings)
- [ ] `python -m app.cli project validate ATLAS`
- [ ] `cd assistant-core` → `python -m pytest -q`
- [ ] `python -m app.cli safety show`
- [ ] `python -m app.cli mcp list`
- [ ] `python -m app.cli mcp generate --target all --dry-run` (no file writes)
- [ ] Controlled `mcp generate` (without `--dry-run`) when configs change
- [ ] `python -m app.cli command preview ATLAS --type test`
- [ ] `python -m app.cli report create ATLAS --type system-health`
- [ ] `python -m app.cli audit v1-rc` (when memory DB initialized)
