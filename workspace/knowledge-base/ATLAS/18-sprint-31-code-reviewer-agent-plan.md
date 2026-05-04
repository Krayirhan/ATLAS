# Sprint 31 - CodeReviewerAgent Alpha

## Sprint 31 amaci

ATLAS icine read-only calisan, scope bazli ve bounded bir `CodeReviewerAgent` eklemek.

## CodeReviewerAgent rolu

- Kod, config, test ve dokumantasyon dosyalarini sinirli scope icinde inceler.
- Bulgu, risk, iyilestirme onerisi ve test onerisi uretir.
- Uygulama yapmaz; review-only kalir.

## Scope listesi

- `safety`
- `ai-layer`
- `config`
- `mcp`
- `tests`
- `docs`
- `architecture`
- `all-light`

## Kapsam

- Scope bazli izinli dosya listesi
- Bounded file count ve char limit
- `ai review` CLI komutu
- Mock ve Ollama provider destegi
- Structured findings / recommendations / test suggestions

## Kapsam disi

- Kod yazmak
- Dosya degistirmek
- Terminal komutu calistirmak
- Git / MCP tool cagrisi yapmak
- Full repo unbounded scan

## CLI komutlari

```text
python -m app.cli ai review --project ATLAS --provider mock --scope safety
python -m app.cli ai review --project ATLAS --provider mock --scope ai-layer --show-sources
python -m app.cli ai review --project ATLAS --provider ollama --scope config
```

## Guvenlik sinirlari

- Read-only only
- Dosya yazma yok
- Terminal run yok
- Git / MCP tool call yok
- `.env` / key / browser profile okuma yok
- Prompt full logging yok

## Test plani

- Unit tests for scope filtering
- Mock provider review tests
- Ollama timeout graceful warning tests
- CLI JSON and show-sources tests
- Existing `ai ask-agent` / `ai plan` regression smoke tests

## Acceptance criteria

- `CodeReviewerAgent` olusur
- `ai review` komutu calisir
- `--scope safety` ve `--scope ai-layer` calisir
- `--show-sources` ve `--json` calisir
- Full repo scan yapmaz
- Read-only boundary korunur

## Sprint 32 bagimliligi

- `ToolApproval Design`
