# ATLAS V1 RC GO Report

**Title:** ATLAS V1 RC GO Report  
**Date (last doc refresh):** 2026-05-04  
**Canonical root:** `E:\ATLAS`  
**Self-project:** **ATLAS** (`python-cli`)

---

## Executive summary

V1 Release Candidate is **GO** for the control-plane scope: configs, safety, registry, MCP generation rules, memory, reports, doctor, and audit automation. **Sprints 25–27** completed documentation, test hardening, and report/audit polish **without** adding any LLM provider, `ai ask`, or autonomous agents.

---

## Registry status

- Primary entry: **ATLAS** at monorepo root `E:\ATLAS`, knowledge `E:\ATLAS\workspace\knowledge-base\ATLAS`, `command_workdir` = `assistant-core` for pytest/doctor-style commands.
- **BenimFormum** is **not** registered and is **not** the pilot.
- Legacy smoke names (e.g. AtlasSmokeProject) are **not** part of the supported self-project registry.

---

## Test status

- Last automated run (representative): **`python -m pytest -q`** from `E:\ATLAS\assistant-core` — **34 passed** (Sprint 26 coverage batch).

---

## Doctor status

- `python -m app.cli doctor` — expected **OK** on a healthy tree.
- `python -m app.cli doctor --full` — expected **OK**; optional toolchain rows (node/npm/git/docker) may warn on minimal machines without failing RC.

---

## Audit status

- `python -m app.cli audit v1-rc` — runs config validation, optional integration partition (critical vs optional tooling gaps), **pytest** probe, and checks generated MCP does not advertise `D:\ATLAS` as workspace. Verdict is **GO** when no critical blockers remain.

---

## MCP status

- `mcp.master.json` + `mcp generate` keep `workspace-filesystem` on **`E:\ATLAS\workspace` only** (validated in `config validate`).
- **`D:\ATLAS`** must not appear as an MCP workspace path in generated configs.

---

## Safety status

- Blocked commands include destructive git patterns, `Remove-Item -Recurse`, `Invoke-Expression`, etc.
- Blocked file patterns cover `.env`, key material filenames/extensions, and similar.
- **`D:\ATLAS`** may be listed under blocked paths as a legacy-path guard (not a whole-drive ban of all `D:` paths).

---

## Known limitations

- MCP helper scripts are **not** full production MCP stdio servers.
- Context token numbers are **budgets / plans**, not measured provider tokens.
- Reports remain partially template-driven; deeper narrative is **V1.1+**.

---

## Next sprints

| Sprint | Theme |
|--------|--------|
| **26** | (closed in batch) Test coverage hardening |
| **27** | (closed in batch) Report depth + integration polish |
| **28** | **AI Layer Foundation** — provider interfaces, prompt composer, read-only `ai ask` design (**no** file write / terminal run / orchestration yet) |
| **29** | MemoryAgent / ProjectQAAgent |
| **30** | PlannerAgent |
| **31** | CodeReviewerAgent |
| **32** | Tool approval design |
| **33** | MainAgent alpha |

---

## References

- Checklist: `05-release-checklist.md`
- Status / risks / backlog: `03-current-status.md`, `04-risk-list.md`, `06-next-sprints.md`
