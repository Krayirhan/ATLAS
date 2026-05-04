# ATLAS — V1 RC checklist

- [ ] `python -m app.cli config validate`
- [ ] `python -m app.cli doctor`
- [ ] `python -m app.cli doctor --full` (optional tool warnings acceptable)
- [ ] `python -m app.cli project validate ATLAS`
- [ ] `cd E:\ATLAS\assistant-core` → `python -m pytest -q`
- [ ] `python -m app.cli safety show`
- [ ] `python -m app.cli mcp list`
- [ ] `python -m app.cli mcp generate --target all --dry-run` (no writes)
- [ ] `python -m app.cli memory sync-projects`
- [ ] `python -m app.cli command preview ATLAS --type test`
- [ ] `python -m app.cli integrations check ATLAS` (optional gaps may warn without failing)
- [ ] `python -m app.cli report create ATLAS --type system-health`
- [ ] `python -m app.cli audit v1-rc` → **GO** or documented **CONDITIONAL**

See also: `07-v1-rc-go-report.md`.
