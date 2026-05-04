# Sprint 29 - MemoryAgent + ProjectQAAgent Alpha

## Purpose

Add two thin, read-only helpers on top of the Sprint 28 AI layer:

- `MemoryAgent`
- `ProjectQAAgent`

## What they are not

- Not autonomous coding agents
- Not planners or patch appliers
- Not tool runners or terminal executors

They stay read-only and return natural language plus safe source metadata.

## Relationship to context loader

Both agents reuse the same approved source contract as Sprint 28. They do not scan the whole repo. They weight memory, KB, and recent reports differently depending on the task.

## Sources

- Registry
- memory repository summaries
- KB markdown
- curated recent reports

Same allowed set as Sprint 28, with the same blocked-source rules.

## CLI examples (implemented in Sprint 29)

```text
python -m app.cli ai memory --project ATLAS
python -m app.cli ai ask-agent --project ATLAS --provider mock "ATLAS su an ne durumda?"
python -m app.cli ai ask-agent --project ATLAS --provider ollama "Sprint 30'a gecilebilir mi?"
```

## Outcome

- `MemoryAgent` produces a bounded read-only project snapshot.
- `ProjectQAAgent` answers project questions from approved sources only.
- Existing `ai ask` flow remains intact.
- Agent surface stays read-only: no file writes, no terminal execution, no git, no MCP tool calls.

## Out of scope

- Terminal, file write, git, MCP tool calls
- Planner loops and code patch application
- Multi-step autonomous workflows

## Exit criteria (alpha)

- Documented behavior and tests for memory-only and KB-only questions
- Fails closed when a question would require blocked sources
- CLI commands `ai memory` and `ai ask-agent` available
