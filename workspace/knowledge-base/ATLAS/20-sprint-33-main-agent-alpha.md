# Sprint 33 - MainAgent Alpha

## Sprint 33 amaci

ATLAS icine read-only bir koordinator agent eklemek.

## MainAgent rolu

- Kullanici istegini siniflandirir.
- Uygun alt agentlari secer.
- Sonuclari birlestirir.
- Preview-only kalir.

## Routing mantigi

- Project question/status -> `MemoryAgent` + `ProjectQAAgent`
- Sprint plan -> `MemoryAgent` + `PlannerAgent`
- Review/security review -> `MemoryAgent` + `CodeReviewerAgent`
- Approval check -> `ToolApprovalAgent`
- Unknown -> graceful fallback

## Alt agentlar

- `MemoryAgent`
- `ProjectQAAgent`
- `PlannerAgent`
- `CodeReviewerAgent`
- `ToolApprovalAgent`

## Kapsam

- Deterministic routing
- Bounded orchestration
- Source / warning aggregation
- Approval preview coordination

## Kapsam disi

- Command execution
- File write
- Git / MCP operations
- Autonomous workflow
- Approval token production

## CLI komutlari

```text
python -m app.cli ai main --project ATLAS --provider mock "ATLAS şu an ne durumda?"
python -m app.cli ai main --project ATLAS --provider mock --show-routing "Sprint 34 için plan çıkar"
python -m app.cli ai main --project ATLAS --provider mock --show-routing "git reset --hard güvenli mi?"
python -m app.cli ai main --project ATLAS --provider ollama "AI layer güvenli mi?"
```

## Guvenlik sinirlari

- Read-only only
- File write yok
- Terminal run yok
- MCP tool call yok
- Approval token yok
- Prompt full logging yok

## Test plani

- MainAgent routing unit tests
- CLI routing/source/json tests
- Existing ai plan / ai review / ai approval regression tests

## Acceptance criteria

- `MainAgent` olusur
- `ai main` komutu calisir
- Project / plan / review / approval route'lari dogru secilir
- Hicbir execution yuzeyi acilmaz

## Sprint 34 bagimliligi

- `SecurityAuditorAgent`
