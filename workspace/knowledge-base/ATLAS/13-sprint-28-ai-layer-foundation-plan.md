# Sprint 28 — Ollama AI Layer Foundation + Read-only AI Ask

## Goal

Introduce a **minimal, read-only** AI surface on top of the existing control plane: **Ollama** as default provider, **`ai doctor`** for local checks, **`ai ask`** for advisory answers using the **context contract** (`11-ai-context-contract.md`). No agents, no tool calling, no file or terminal side effects.

## In scope

- Ollama HTTP client (loopback) with timeouts.
- Context assembly from **allowed sources** only (`16-ai-source-index.md`).
- CLI commands: `ai doctor`, `ai ask` (read-only).
- Tests: `tests/test_ai_*.py` (unit + mocked HTTP where needed).
- Documentation updates after implementation.

## Out of scope

- OpenAI / cloud providers (optional later sprint).
- RAG, vector stores, embeddings pipelines.
- MemoryAgent / ProjectQAAgent / PlannerAgent / CodeReviewerAgent (Sprint 29+).
- Autonomous patch application, terminal, MCP execution.

## Planned code layout (Sprint 28 — not implemented in Sprint 27.5)

```text
assistant-core/app/ai/
├── __init__.py
├── config.py           # pydantic / dataclass for ai.* settings
├── ollama_client.py    # minimal HTTP wrapper
├── context_assembler.py
└── prompts.py          # system + user templates from 12-ai-prompt-policy.md

assistant-core/app/commands/ai.py   # Typer: ai doctor, ai ask
```

## Config additions (design)

| Key | Example |
|-----|---------|
| `ai.default_provider` | `ollama` |
| `ollama.base_url` | `http://localhost:11434` |
| `ollama.default_model` | `qwen2.5:7b` |
| `ollama.request_timeout_seconds` | `120` |

*(Exact JSON file name TBD in Sprint 28 — may extend `assistant.settings.json` or add `configs/ai.settings.json` with loader validation.)*

## Security boundaries

See `15-ai-security-boundaries.md`. Sprint 28 must not violate read-only or blocked-source rules.

## Acceptance criteria (Sprint 28 exit)

- `python -m app.cli ai doctor` returns actionable status when Ollama is up/down and model missing/present.
- `python -m app.cli ai ask --project ATLAS "…"` returns an answer grounded in allowed context or states insufficient context.
- No file writes, no subprocess terminal runs, no MCP invocations from `ai` commands.
- `python -m pytest -q` passes; `doctor --full`, `config validate`, `project validate ATLAS`, `audit v1-rc` pass.

## Test plan (high level)

- Mock Ollama HTTP for success, 404 model, connection refused, timeout.
- Golden tests for context assembler ordering vs `11-ai-context-contract.md`.
- CLI smoke for `ai doctor` / `ai ask` with fakes.

## Final validation commands (Sprint 28 closeout)

```text
cd E:\ATLAS\assistant-core
python -m pytest -q
python -m app.cli doctor --full
python -m app.cli config validate
python -m app.cli project validate ATLAS
python -m app.cli ai doctor
python -m app.cli ai ask --project ATLAS "Özet durum nedir?"
python -m app.cli audit v1-rc
```

## Dependency on Sprint 29

Sprint 29 agents consume the same context contract; Sprint 28 must freeze the assembler API enough for thin wrappers.
