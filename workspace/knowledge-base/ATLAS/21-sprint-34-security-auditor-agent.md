# Sprint 34 - SecurityAuditorAgent

## Sprint 34 amaci

ATLAS icine read-only calisan ilk guvenlik denetim agentini eklemek.

## SecurityAuditorAgent rolu

- agent capability flag denetimi
- MCP exposure denetimi
- approval policy denetimi
- context source ve prompt logging riski denetimi
- docs / KB alignment kontrolu
- deterministic GO / CONDITIONAL / NO-GO karari

## Scope listesi

- `agents`
- `mcp`
- `secrets`
- `approval`
- `context`
- `docs`
- `all-light`

## Kapsam

- bounded file reads
- structured findings
- security controls ozeti
- test suggestions
- MainAgent security route entegrasyonu

## Kapsam disi

- dosya degistirme
- terminal komutu calistirma
- Git islemi
- MCP tool cagrisi
- approval token uretimi
- auto-remediation

## CLI komutlari

```powershell
python -m app.cli ai security-audit --project ATLAS --provider mock --scope all-light
python -m app.cli ai security-audit --project ATLAS --provider mock --scope agents --show-sources
python -m app.cli ai security-audit --project ATLAS --provider mock --scope mcp
python -m app.cli ai security-audit --project ATLAS --provider mock --scope approval
python -m app.cli ai main --project ATLAS --provider mock --show-routing "ATLAS guvenli mi?"
```

## Guvenlik sinirlari

- read-only
- dosya yazma yok
- terminal run yok
- Git/MCP tool call yok
- prompt full logging yok
- bounded scope disina cikma yok

## Test plani

- pytest regression
- `ai security-audit` CLI checks
- MainAgent security route checks
- approval policy canonical decision checks
- MCP bounded root checks

## Acceptance criteria

- SecurityAuditorAgent olusur
- `ai security-audit` calisir
- `all-light`, `agents`, `mcp`, `approval` scope'lari calisir
- `--show-sources` calisir
- `--json` calisir
- MainAgent `ATLAS guvenli mi?` sorusunu SecurityAuditorAgent'a route eder
- full repo scan yapmaz
- read-only sinir korunur

## Sprint 35 bagimliligi

- DocumentationAgent
