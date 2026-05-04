# Ollama Integration Plan

Sprint 28.6 note: first model load may be slow; `ai warmup`, `keep_alive`, and a `300s` timeout are used to harden live runtime behavior.

## Default local LLM provider

**Ollama** is the **default** local LLM provider for ATLAS’s first AI layer: it aligns with **local-first** operation and avoids cloud API keys in the default path.

## Base URL and models

| Setting | Value |
|---------|--------|
| **Base URL** | `http://localhost:11434` |
| **First recommended model** | `qwen2.5:7b` |
| **Alternative (code-oriented)** | `qwen2.5-coder:7b` |

## Why local LLM first?

- **No API key** for the default Ollama loop (keys stay out of `.env` for this path).
- **No `.env` requirement** for basic Ollama usage (still: never commit secrets).
- **Offline / air-gap friendly** once models are pulled.
- **Fits ATLAS safety stance**: network can stay on loopback; policy can treat non-local endpoints as out-of-scope until explicitly configured.

## Health and CLI (design — Sprint 28)

| Command (planned) | Intent |
|-------------------|--------|
| `python -m app.cli ai doctor` | Check Ollama daemon reachability, model presence, latency smoke, config alignment. |
| `python -m app.cli ai ask --project ATLAS "…"` | Read-only question with **assembled context** per `11-ai-context-contract.md`; **no** file/terminal/tool side effects. |

## Example Ollama maintenance commands

```text
ollama --version
ollama list
ollama pull qwen2.5:7b
```

Example ATLAS CLI (after Sprint 28 implementation):

```text
python -m app.cli ai doctor
python -m app.cli ai ask --project ATLAS "ATLAS şu an ne durumda?"
```

## Failure scenarios (operational playbook)

| Scenario | Mitigation |
|----------|------------|
| Ollama not installed | `ai doctor` reports install hint; `ai ask` refuses with clear message. |
| Ollama not running | Connection error; document start (`ollama serve` / OS service). |
| Model missing | `ai doctor` lists `ollama list`; suggest `ollama pull …`. |
| Slow responses | Timeouts + user messaging; reduce context size per contract. |
| Timeouts | Configurable timeout; degrade to “partial answer” or abort with reason. |

## Explicitly out of scope for this documentation sprint (and early AI)

- Model fine-tuning.
- RAG / vector index.
- Tool calling from the model.
- Multi-agent orchestration.

## References

- Sprint 28 plan: `13-sprint-28-ai-layer-foundation-plan.md`
- Security: `15-ai-security-boundaries.md`
