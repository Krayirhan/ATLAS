# NotebookLM exports (ATLAS)

Bu klasör **NotebookLM’den manuel** alınan özet markdown dosyaları içindir. ATLAS **NotebookLM API’sine bağlanmaz**; bu akış tamamen dosya tabanlıdır.

## Kurallar

- **Secret koymayın** (API key, token, parola, private URL parametreleri).
- Ham private dokümanların tam metnini buraya kopyalamayın; **özet** kullanın.
- Özetleri `_templates` altındaki şablonlara uygun biçimde düzenleyin.

## Klasör yapısı

```text
E:\ATLAS\workspace\notebooklm-exports
├── README.md
├── _templates
│   ├── atlas-notebooklm-export-template.md
│   ├── project-summary-export-template.md
│   ├── sprint-report-export-template.md
│   └── risk-audit-export-template.md
└── incoming-exports    # elle bırakılan dosyalar (işlendikten sonra arşivlenebilir)
```

## Import komutları

```powershell
cd E:\ATLAS\assistant-core

python -m app.cli notebooklm list
python -m app.cli notebooklm import ATLAS --source E:\ATLAS\workspace\notebooklm-exports\<dosya>.md
python -m app.cli notebooklm validate ATLAS
```

Detaylı akış: `workspace/knowledge-base/ATLAS/10-notebooklm-workflow.md`.
