# assistant-core

ATLAS core uygulama katmani.

## AI Layer / Ollama

Sprint 28 ile read-only AI foundation eklendi. Sprint 28.6 ile runtime hardening yapildi.

- Varsayilan provider: `ollama`
- Test ve fallback provider: `mock`
- Kapsam: `ai doctor`, `ai ask`
- Guvenlik sinirlari:
  - AI read-only advisory mode
  - terminal execution yok
  - dosya yazan AI yok
  - tool calling yok
  - git automation yok
- Ilk Ollama cagrisi model load nedeniyle yavas olabilir.
- `ai warmup` modeli onceden yukleyebilir.
- `keep_alive` modelin bellekte kalmasina yardimci olur.
- Ollama timeout degeri `300s` olarak artirildi.

### Ornek komutlar

```powershell
ollama list
ollama pull qwen2.5:7b
python -m app.cli ai doctor
python -m app.cli ai warmup --provider ollama
python -m app.cli ai ask --project ATLAS "ATLAS su an ne durumda?"
python -m app.cli ai ask --project ATLAS --provider mock "ATLAS su an ne durumda?"
```

## CodeReviewerAgent Alpha

Sprint 31 ile `CodeReviewerAgent` Alpha geldi.

- Read-only review uretir.
- Kod yazmaz.
- Dosya degistirmez.
- Terminal calistirmaz.
- Git/MCP tool cagrisi yapmaz.
- Scope bazli sinirli dosya okur.

Komut ornekleri:

```powershell
python -m app.cli ai review --project ATLAS --provider mock --scope safety
python -m app.cli ai review --project ATLAS --provider ollama --scope ai-layer --show-sources
python -m app.cli ai review --project ATLAS --provider ollama --scope config
```

## ToolApproval Design

Sprint 32 ile `ToolApprovalAgent` geldi.

- Komutlari calistirmaz.
- Sadece karar ve preview uretir.
- `blocked`, `approval_required`, `preview_allowed`, `safe_readonly` kararlarini verir.
- Kullanici onayi olmadan hicbir tool calismaz.

Komut ornekleri:

```powershell
python -m app.cli ai approval command --project ATLAS --cmd "python -m pytest -q"
python -m app.cli ai approval command --project ATLAS --cmd "git reset --hard"
python -m app.cli ai approval command --project ATLAS --cmd "git push"
```

### Ollama onkosulu

- Default endpoint: `http://localhost:11434`
- Default model: `qwen2.5:7b`
- Ollama kurulu degilse mock provider ile testler yine calisir.
- Model yoksa pull islemi otomatik yapilmaz; onerilen komut:

```powershell
ollama pull qwen2.5:7b
```

## Agents Alpha

Sprint 29 ile `MemoryAgent` ve `ProjectQAAgent` Alpha geldi.

- Read-only agentlardir.
- Kod yazmazlar.
- Dosya degistirmezler.
- Terminal calistirmazlar.
- Git/MCP tool cagrisi yapmazlar.

Kullanim:

```powershell
python -m app.cli ai memory --project ATLAS
python -m app.cli ai ask-agent --project ATLAS --provider mock "ATLAS su an ne durumda?"
python -m app.cli ai ask-agent --project ATLAS --provider ollama "Sprint 30'a gecilebilir mi?"
```

## PlannerAgent Alpha

Sprint 30 ile `PlannerAgent` Alpha geldi.

- Read-only plan uretir.
- Kod yazmaz.
- Dosya degistirmez.
- Terminal calistirmaz.
- Git/MCP tool cagrisi yapmaz.

Komut ornekleri:

```powershell
python -m app.cli ai plan --project ATLAS --provider mock --goal "Sprint 31 için CodeReviewerAgent planla"
python -m app.cli ai plan --project ATLAS --provider ollama --goal "ATLAS için test coverage sprinti planla"
```
