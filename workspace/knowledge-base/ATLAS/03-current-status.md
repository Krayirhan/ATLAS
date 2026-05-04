# ATLAS — Current status (Sprint 24)

- **V1 skeleton:** Present — CLI, config loader, safety, MCP generator, registry, memory, notebooklm/context/report/doctor/audit wiring.
- **Root:** `E:\ATLAS` (canonical). `D:\ATLAS` is **not** used.
- **Self-project registry:** **ATLAS** registered as `python-cli` with `command_workdir` = `assistant-core` for pytest/doctor commands.
- **Pilot:** **ATLAS** is the self-project. BenimFormum is **not** the pilot.
- **Tests:** Last `python -m pytest -q` (Sprint 24): **14 passed** (from `E:\ATLAS\assistant-core`).
- **Doctor:** Run `python -m app.cli doctor` and `python -m app.cli doctor --full`; optional tool warnings (node/npm/git/docker) are expected on minimal machines and are non-blocking for V1 RC.
