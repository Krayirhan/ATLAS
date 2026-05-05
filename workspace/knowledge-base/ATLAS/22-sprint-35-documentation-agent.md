# Sprint 35 — DocumentationAgent

**Tarih:** 2026-05-06  
**Durum:** GO  
**Sprint:** 35  
**Canonical root:** `E:\ATLAS`

---

## Amaç

ATLAS içine `DocumentationAgent` eklemek.  
`DocumentationAgent` **read-only** bir dokümantasyon audit ajanıdır.

---

## DocumentationAgent Rolü

- README.md ve assistant-core/README.md güncel mi kontrol eder
- knowledge-base dosyaları tutarlı mı kontrol eder
- Sprint 28–34 durumları doğru işlenmiş mi kontrol eder
- NotebookLM workflow dokümantasyonu var mı kontrol eder
- AI/agent roadmap doğru mu kontrol eder
- V1 / V2 / V3 kapsam ayrımı korunuyor mu kontrol eder
- Eksik sprint dokümanlarını tespit eder
- Dokümantasyon risklerini ve önerilerini raporlar
- GO / CONDITIONAL / NO-GO dokümantasyon kararı üretir

**DocumentationAgent asla:**
- Dosya değiştirmez
- Kod yazmaz
- Terminal çalıştırmaz
- Git işlemi yapmaz
- MCP tool çağırmaz
- Approval token üretmez

---

## Scope Listesi

| Scope | Kontrol Edilen Dosyalar |
|-------|-------------------------|
| `readme` | README.md, assistant-core/README.md |
| `knowledge-base` | 00-project-summary, 03-current-status, 04-risk-list, 06-next-sprints, 07-v1-rc-go-report |
| `notebooklm` | 10-notebooklm-workflow + notebooklm-exports templates |
| `roadmap` | 06-next-sprints, 07-v1-rc-go-report, README.md |
| `agents` | Sprint docs 14–21 + README.md |
| `release` | 05-release-checklist, 07-v1-rc-go-report |
| `all-light` | README, current-status, next-sprints, v1-rc-go-report, notebooklm-workflow, sprint docs 14–21 |

---

## Kapsam

- DocumentationAgent oluşturuldu: `assistant-core/app/agents/documentation_agent.py`
- Agent modelleri eklendi: `models.py`
  - `DocumentationAuditRequest`
  - `DocumentationAuditResult`
  - `DocumentationFinding`
  - `DocumentationAuditScope`
  - `DocumentationAuditCategory`
  - `DocumentationAuditSeverity`
  - `DocumentationAuditDecision`
  - `DocumentationSourceCheck`
  - `DocumentationRoadmapCheck`
  - `DocumentationConsistencyCheck`
  - `DocumentationRecommendation`
- CLI komutu eklendi: `ai docs-audit`
- MainAgent routing güncellendi: `readme`, `dokuman`, `notebooklm`, `roadmap` keywords → DocumentationAgent
- SecurityAuditorAgent capability check güncellendi: DocumentationAgent dahil edildi

---

## Kapsam Dışı

- Dokümanları otomatik güncelleme
- README veya KB dosyalarını değiştirme
- Komut çalıştırma
- Git işlemi
- MCP tool çağırma
- Secret dosya okuma
- Full repo / full disk tarama

---

## CLI Komutları

```bash
# Genel audit (all-light)
python -m app.cli ai docs-audit --project ATLAS --provider mock --scope all-light

# README kontrolü + kaynak listesi
python -m app.cli ai docs-audit --project ATLAS --provider mock --scope readme --show-sources

# NotebookLM workflow kontrolü
python -m app.cli ai docs-audit --project ATLAS --provider mock --scope notebooklm

# Agent sprint dokümanları kontrolü
python -m app.cli ai docs-audit --project ATLAS --provider mock --scope agents

# JSON çıktı
python -m app.cli ai docs-audit --project ATLAS --provider mock --scope all-light --json

# Roadmap kontrolü (Ollama)
python -m app.cli ai docs-audit --project ATLAS --provider ollama --scope roadmap

# MainAgent üzerinden (routing)
python -m app.cli ai main --project ATLAS --provider mock --show-routing "README guncel mi?"
```

---

## Güvenlik Sınırları

- `read_only = True`
- `can_write_files = False`
- `can_run_commands = False`
- `can_call_tools = False`
- `.env`, `*.pem`, `*.key`, `id_rsa`, `id_ed25519` okumaz
- `D:\ATLAS` erişimi engellendi
- `C:\Users` tam tarama engellendi
- Full repo unbounded scan yapılmaz
- `**` glob kullanılmaz
- Approval token üretilmez
- Prompt tam loglanmaz (`prompt_logged: False`)

---

## Test Planı

Oluşturulan test dosyaları:
- `tests/test_documentation_agent.py` — 32 test
- `tests/test_ai_docs_audit_cli.py` — 21 test

Kapsanan senaryolar:
- read_only, can_write_files, can_run_commands, can_call_tools flag'leri
- all-light, readme, notebooklm, agents, roadmap, release, knowledge-base scope'ları
- unknown scope → graceful error
- .env, D:\ATLAS, *.pem okuma engeli
- Full repo scan yok (** glob yok)
- max_files ve max_chars_per_file sınırları
- Structured findings ve decision
- Ollama monkeypatch
- Ollama timeout → graceful warning
- Source metadata
- --json geçerli JSON üretir
- --show-sources çalışır
- "README güncel mi?" → documentation-agent route
- Mevcut komutlar bozulmadı (ai main, ai security-audit)
- approval_token_in_result yok
- prompt_logged False

---

## Acceptance Criteria

- [x] DocumentationAgent oluşturuldu
- [x] DocumentationAgent read_only = True
- [x] ai docs-audit komutu çalışıyor
- [x] --scope all-light çalışıyor
- [x] --scope readme çalışıyor
- [x] --scope notebooklm çalışıyor
- [x] --scope agents çalışıyor
- [x] --show-sources çalışıyor
- [x] --json çalışıyor
- [x] MainAgent "README güncel mi?" → DocumentationAgent
- [x] README / KB / NotebookLM / roadmap / agent docs kontrol ediliyor
- [x] Full repo scan yok
- [x] Dosya yazmıyor
- [x] Terminal çalıştırmıyor
- [x] MCP tool çağırmıyor
- [x] Approval token üretmiyor
- [x] .env / private key okumıyor
- [x] pytest geçiyor (211 passed)
- [x] doctor --full geçiyor
- [x] audit v1-rc GO veriyor
- [x] security-audit all-light GO veriyor

---

## Sprint 36 Bağımlılığı

**Sprint 36 — ReportAgent**

ReportAgent, mevcut report generator üzerine bir read-only AI agent katmanı ekler.
DocumentationAgent'ın audit sonuçlarını okuyabilir ve raporlara dahil edebilir.
