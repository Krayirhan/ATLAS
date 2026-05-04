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

### Ollama onkosulu

- Default endpoint: `http://localhost:11434`
- Default model: `qwen2.5:7b`
- Ollama kurulu degilse mock provider ile testler yine calisir.
- Model yoksa pull islemi otomatik yapilmaz; onerilen komut:

```powershell
ollama pull qwen2.5:7b
```
