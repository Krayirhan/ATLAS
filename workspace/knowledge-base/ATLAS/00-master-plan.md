# ATLAS AI Assistant — Uçtan Uca Tasarım, Mimari ve Sprint Sistemi

> **Proje Root:** `E:\ATLAS`  
> **Hedef Platform:** Windows + PowerShell  
> **Yaklaşım:** Security-first, local-first, token-aware, audit-log destekli developer AI control plane  
> **Durum:** Kodlamaya başlamadan önce mimari ve uygulama planı

---

## 0. Kısa Özet

**ATLAS AI Assistant**, Cursor, Codex, GitHub Copilot, NotebookLM, MCP server’lar, local memory, proje knowledge-base’i ve güvenli terminal/build/test akışlarını tek merkezde birleştiren kişisel geliştirici asistan altyapısıdır.

Bu sistem bir chatbot değildir. Asıl amaç, farklı AI araçlarının aynı proje bilgisine, aynı kurallara, aynı güvenlik politikalarına ve aynı context üretim mantığına dayanmasını sağlamaktır.

Temel fikir şudur:

```text
Cursor + Codex + GitHub Copilot + NotebookLM + MCP + Local Memory
        ↓
Tek merkezi proje hafızası
        ↓
Tek ortak instruction sistemi
        ↓
Tek güvenli MCP/tool katmanı
        ↓
Token kontrollü developer AI assistant
```

V1 aşamasında hedef, otomatik kod yazan tam agent sistemi değil; güvenli, kontrollü ve sürdürülebilir bir **AI developer control plane** kurmaktır.

---

## 1. Projeyi Nasıl Anlıyorum?

ATLAS, kişisel yazılım geliştirme ekosistemini merkezileştirmek için tasarlanan bir altyapıdır. Kullanıcı şu anda farklı projelerde farklı AI araçlarını ayrı ayrı kullanmaktadır:

- Cursor
- Codex
- GitHub Copilot
- NotebookLM
- MCP server’lar
- Lokal proje klasörleri
- GitHub repoları
- Android, ML/MLOps, Unity, Java, Spring Boot projeleri

Mevcut problem şudur:

```text
Her araç ayrı bağlamla çalışıyor.
Her proje için kurallar elle tekrar yazılıyor.
NotebookLM çıktıları sistematik biçimde projelere bağlanmıyor.
Build/test/lint komutları güvenli merkezi bir katmandan geçmiyor.
AI araçları bazen çok fazla dosya okuyarak token tüketimini artırıyor.
Riskli terminal komutları için merkezi politika yok.
Projelerin durum bilgisi kalıcı ve sorgulanabilir bir memory sisteminde tutulmuyor.
```

ATLAS bu problemi şu şekilde çözecek:

```text
1. Projeleri registry içine kaydedecek.
2. Her proje için knowledge-base oluşturacak.
3. NotebookLM özetlerini knowledge-base’e aktaracak.
4. Cursor, Codex ve Copilot için ortak instruction dosyaları üretecek.
5. MCP configlerini tek master config’ten üretecek.
6. Build/test/lint komutlarını whitelist ve safety policy ile kontrol edecek.
7. Riskli komutları engelleyecek.
8. Her işlem için audit log tutacak.
9. Context manager ile token tasarruflu okuma sırası uygulayacak.
10. V2’de gerçek agent orchestrator katmanına zemin hazırlayacak.
```

---

## 2. Ana Tasarım İlkeleri

### 2.1 Security First

ATLAS’ta güvenlik otomasyondan daha önemlidir. Sistem şu prensiple çalışmalıdır:

```text
Önce oku → sonra planla → sonra preview et → sonra kullanıcı onayı iste → sonra uygula/logla
```

V1’de terminal komutları mümkün olduğunca **preview** seviyesinde kalmalıdır. Gerçek çalıştırma yetkisi ancak daha sonraki sprintlerde ve approval token ile sınırlandırılmış şekilde düşünülmelidir.

### 2.2 Local First

ATLAS, Windows PC üzerinde lokal çalışan bir sistemdir. Proje bilgisi, memory DB, knowledge-base, logs ve configler `E:\ATLAS` altında tutulur.

### 2.3 Token Aware

ATLAS, büyük projeyi ilk hamlede LLM’e basmamalıdır. Okuma sırası daima şu mantıkta olmalıdır:

```text
1. Project registry
2. SQLite memory
3. knowledge-base/00-project-summary.md
4. İlgili knowledge-base dosyası
5. Son raporlar
6. Gerekirse gerçek proje dosyası
```

### 2.4 Tool Specific, Source Unified

Cursor, Codex ve Copilot’un yetenekleri aynı değildir. Bu yüzden ATLAS “her araç aynı memory DB’ye canlı bağlanacak” varsayımıyla değil, şu yaklaşımla tasarlanmalıdır:

```text
Central Memory → Generated Instructions → Tool-specific Context
```

Yani merkezi bilgi ATLAS’ta tutulur, araçlara uygun formatlarda instruction/context dosyaları üretilir.

### 2.5 Audit Everything

Önemli işlemler JSONL log olarak tutulmalıdır:

- config validate
- mcp generate
- project add
- instructions generate
- notebooklm import
- memory update
- context build
- command preview
- onboard
- integration check
- report create

### 2.6 No Hidden Dangerous Automation

ATLAS kesinlikle şunları yapmamalıdır:

- Tüm diski MCP’ye açmak
- `C:\Users` klasörünü komple açmak
- `.env` okumak
- private key, SSH key, keystore, JKS dosyalarını okumak
- otomatik dosya silmek
- `git reset --hard` çalıştırmak
- `git clean -fd` çalıştırmak
- `git push --force` çalıştırmak
- production deploy otomasyonu eklemek
- Copilot Cloud Agent’a write/terminal yetkisi vermek
- büyük projeyi komple LLM’e basmak
- NotebookLM’i runtime bağımlılığı yapmak

---

## 3. Nihai Mimari

ATLAS mimarisini 6 ana katman olarak düşünmek en sağlıklısıdır.

```text
E:\ATLAS
│
├── 1) Control Plane
│   ├── Python CLI
│   ├── doctor
│   ├── config validate
│   ├── paths
│   └── onboarding
│
├── 2) Project Intelligence Layer
│   ├── project-registry.json
│   ├── SQLite memory
│   ├── knowledge-base
│   ├── notebooklm imports
│   └── analysis reports
│
├── 3) Context Manager
│   ├── task type detection
│   ├── token budget
│   ├── context read plan
│   └── summary-first strategy
│
├── 4) Instruction Generator
│   ├── AGENTS.md
│   ├── .cursor/rules/*.mdc
│   ├── .github/copilot-instructions.md
│   ├── .github/instructions/*.instructions.md
│   └── .codex/config.toml
│
├── 5) Tool / MCP Layer
│   ├── workspace-filesystem MCP
│   ├── project-memory MCP
│   ├── safe-terminal MCP
│   ├── GitHub MCP
│   └── docs/context MCP
│
└── 6) Safety / Audit / Reports
    ├── safety-policy.json
    ├── blocked command rules
    ├── approval rules
    ├── JSONL logs
    ├── integration checks
    └── report generator
```

---

## 4. Ana Klasör Yapısı

Root daima:

```powershell
E:\ATLAS
```

Önerilen ana yapı:

```text
E:\ATLAS
│
├── assistant-core
│   ├── app
│   ├── agents
│   ├── context
│   ├── memory
│   ├── safety
│   ├── tools
│   ├── prompts
│   └── tests
│
├── workspace
│   ├── projects
│   ├── knowledge-base
│   ├── notebooklm-exports
│   ├── raw-sources
│   ├── memory
│   ├── outputs
│   ├── inbox
│   └── vector-index
│
├── mcp-servers
│   ├── project-memory-mcp
│   ├── safe-terminal-mcp
│   └── docs-index-mcp
│
├── configs
│   ├── assistant.settings.json
│   ├── safety-policy.json
│   ├── mcp.master.json
│   ├── project-registry.json
│   └── generated
│
├── templates
│   ├── AGENTS.md.j2
│   ├── copilot-instructions.md.j2
│   ├── cursor-project-context.mdc.j2
│   ├── codex-config.toml.j2
│   ├── android.instructions.md.j2
│   ├── testing.instructions.md.j2
│   ├── room.instructions.md.j2
│   ├── mlops.instructions.md.j2
│   └── unity.instructions.md.j2
│
├── logs
│   ├── tool-calls
│   ├── approvals
│   ├── errors
│   └── sessions
│
└── backups
    ├── memory-backups
    ├── knowledge-base-backups
    ├── config-backups
    └── repo-file-backups
```

---

## 5. Klasörlerin Sorumlulukları

### 5.1 `assistant-core`

Python uygulamasının ana kodları burada durur.

```text
assistant-core
├── app        → CLI entrypoint, command groups
├── agents    → V2 için agent interface hazırlıkları
├── context   → context manager, token budget, read plan
├── memory    → SQLite models, repositories, migrations
├── safety    → command safety, path safety, policy validation
├── tools     → command preview, mcp config generator, report generator
├── prompts   → system prompt parçaları ve prompt composer
└── tests     → pytest testleri
```

V1’de `agents` klasörü gerçek agent çalıştırmayacak, sadece V2 hazırlığı için placeholder veya interface seviyesinde kalacak.

### 5.2 `workspace`

ATLAS’ın çalışma alanıdır.

```text
workspace/projects           → projelerin kısayol/kayıt/metadata alanı
workspace/knowledge-base     → proje özetleri ve analiz dosyaları
workspace/notebooklm-exports → manuel NotebookLM export dosyaları
workspace/raw-sources        → ham kaynaklar
workspace/memory             → assistant.db
workspace/outputs            → rapor çıktıları
workspace/inbox              → işlenecek yeni dosyalar
workspace/vector-index       → V2 RAG/vector index hazırlığı
```

### 5.3 `mcp-servers`

Özel MCP server kodları burada tutulur.

V1’de öncelik:

```text
project-memory-mcp → read-only memory ve knowledge-base okuma
safe-terminal-mcp  → sadece kayıtlı komutları approval ile çalıştırma/preview
```

### 5.4 `configs`

Sistemin merkezi config dosyaları burada durur.

```text
assistant.settings.json → ana ayarlar
safety-policy.json      → path, command, secret, approval kuralları
mcp.master.json         → tek master MCP config
project-registry.json   → kayıtlı projeler
configs/generated       → üretilmiş tool-specific configler
```

### 5.5 `templates`

Instruction generator burada bulunan Jinja2 template’lerini kullanır.

### 5.6 `logs`

Tüm önemli işlemler JSONL olarak buraya yazılır.

### 5.7 `backups`

Memory, knowledge-base, config ve repo dosyaları için geri dönüş noktaları burada tutulur.

---

## 6. Python Teknoloji Seçimi

Önerilen stack:

```text
Python 3.11 veya 3.12
Typer
Rich
Pydantic
python-dotenv
SQLAlchemy
pytest
Jinja2
SQLite
```

### Neden Typer?

- CLI komutları temiz yazılır.
- PowerShell kullanımına uygundur.
- Alt komut grupları kolay organize edilir.

### Neden Rich?

- Terminal çıktıları okunaklı olur.
- Doctor, validate, report preview gibi çıktılar tablolu gösterilebilir.

### Neden Pydantic?

- Config validation için güçlüdür.
- `project-registry.json`, `safety-policy.json`, `mcp.master.json` doğrulaması netleşir.

### Neden SQLite?

- Lokal-first yapıya uygundur.
- Kurulum gerektirmez.
- Project status, decisions, reports ve tool log metadata için yeterlidir.

---

## 7. Config Sistemi

### 7.1 `assistant.settings.json`

Örnek:

```json
{
  "root": "E:\\ATLAS",
  "workspace_root": "E:\\ATLAS\\workspace",
  "memory_db": "E:\\ATLAS\\workspace\\memory\\assistant.db",
  "default_shell": "powershell",
  "log_level": "info",
  "environment": "local"
}
```

### 7.2 `project-registry.json`

Örnek:

```json
{
  "projects": [
    {
      "name": "AtlasPilot",
      "type": "android-compose-room",
      "root": "D:\\AtlasPilot\\android-app",
      "knowledge": "E:\\ATLAS\\workspace\\knowledge-base\\ATLAS",
      "build_command": ".\\gradlew.bat assembleDebug",
      "test_command": ".\\gradlew.bat testDebugUnitTest",
      "lint_command": ".\\gradlew.bat lint",
      "forbidden_changes": [
        "Do not add INTERNET permission",
        "Do not add cloud SDK",
        "Do not add AI SDK",
        "Do not add Health Connect",
        "Do not add SQLCipher",
        "Do not reintroduce fallbackToDestructiveMigration"
      ]
    }
  ]
}
```

### 7.3 `safety-policy.json`

İçermesi gerekenler:

```json
{
  "allowed_workspace_roots": [
    "E:\\ATLAS\\workspace"
  ],
  "blocked_paths": [
    "C:\\Users",
    "C:\\Windows",
    "AppData"
  ],
  "blocked_file_patterns": [
    ".env",
    "*.pem",
    "*.key",
    "*.keystore",
    "*.jks",
    "id_rsa",
    "id_ed25519"
  ],
  "blocked_commands": [
    "del",
    "rmdir",
    "format",
    "shutdown",
    "git reset --hard",
    "git clean -fd",
    "git push --force",
    "Remove-Item -Recurse",
    "Invoke-Expression"
  ],
  "approval_required_commands": [
    "gradlew.bat",
    "npm install",
    "pip install",
    "git commit",
    "git push",
    "docker run"
  ]
}
```

---

## 8. MCP Tasarımı

### 8.1 Workspace Filesystem MCP

Amaç:

```text
Sadece E:\ATLAS\workspace alanını açmak.
Tüm diski açmamak.
Secret ve sistem klasörlerine erişmemek.
```

Cursor formatı:

```json
{
  "mcpServers": {
    "workspace-filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "E:\\ATLAS\\workspace"
      ]
    }
  }
}
```

VS Code/Copilot formatı:

```json
{
  "servers": {
    "workspace-filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "E:\\ATLAS\\workspace"
      ]
    }
  }
}
```

Codex TOML formatı:

```toml
[mcp_servers.workspace-filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "E:\\ATLAS\\workspace"]
```

### 8.2 Project Memory MCP

V1 hedefi:

```text
Read-only çalışmalı.
Project registry okuyabilmeli.
Knowledge-base okuyabilmeli.
SQLite memory okuyabilmeli.
Source code değiştirmemeli.
Terminal komutu çalıştırmamalı.
```

### 8.3 Safe Terminal MCP

V1 sonlarına doğru gelmeli.

Kurallar:

```text
Sadece registry’de tanımlı build/test/lint/status komutları.
approval_token olmadan run yok.
Riskli komutlar engellenir.
Komut çıktısı loglanır.
```

### 8.4 GitHub MCP

V1’de opsiyonel tutulabilir.

Kurallar:

```text
Repo, issue, PR okuma olabilir.
Token hardcode edilmez.
Environment variable kullanılır.
Write/push/merge yetkisi V1’de verilmez.
```

---

## 9. Token Azaltma ve Context Manager

### 9.1 Okuma Sırası

Her proje sorusunda okuma sırası:

```text
1. Project registry
2. SQLite memory
3. knowledge-base/00-project-summary.md
4. İlgili knowledge-base dosyası
5. Son raporlar
6. Gerekirse gerçek proje dosyası
```

### 9.2 Görev Tipleri

```text
simple_question
project_status
sprint_plan
code_review
release_audit
integration_check
```

### 9.3 Token Budget

```text
simple_question: 4000 token
project_status: 8000 token
sprint_plan: 12000 token
code_review: 25000 token
large_audit: 60000 token
```

### 9.4 Context Build Çıktısı

`context build` komutu doğrudan LLM çağırmayabilir. Önce şunu üretmelidir:

```text
- Task type
- Project name
- Token budget
- Okunacak kaynaklar
- Atlanacak kaynaklar
- Gerekçeler
- Risk uyarıları
```

Örnek:

```powershell
python -m app.cli context build AtlasPilot --task project_status
```

---

## 10. SQLite Memory Tasarımı

DB konumu:

```powershell
E:\ATLAS\workspace\memory\assistant.db
```

### 10.1 Tablolar

```text
projects
project_memories
decisions
tool_calls
analysis_reports
```

### 10.2 `projects`

Saklar:

- proje adı
- proje tipi
- root path
- knowledge path
- created_at
- updated_at
- active flag

### 10.3 `project_memories`

Saklar:

- proje status bilgisi
- sprint notları
- önemli teknik bilgiler
- son doğrulama sonucu

### 10.4 `decisions`

Saklar:

- mimari kararlar
- scope kararları
- güvenlik kararları
- MVP dışı bırakılanlar

### 10.5 `tool_calls`

Saklar:

- hangi komut çağrıldı
- preview mi run mı
- güvenlik sonucu
- timestamp
- proje adı

### 10.6 `analysis_reports`

Saklar:

- rapor tipi
- rapor path’i
- oluşturulma zamanı
- ilişkili proje

---

## 11. Instruction Generator Tasarımı

### 11.1 Cursor İçin

Üretilecek dosyalar:

```text
.cursor/rules/project-context.mdc
.cursor/rules/architecture-rules.mdc
.cursor/rules/testing-rules.mdc
```

Cursor rolü:

```text
- Günlük kodlama
- UI polish
- Hızlı dosya edit
- Küçük refactor
- Ekran bazlı inceleme
```

Cursor genel kuralı:

```text
Önce .cursor/rules ve AGENTS.md oku.
Sonra sadece gerekli dosyaları aç.
Büyük refactor yapma.
Mevcut mimariyi bozma.
Önce kısa plan çıkar.
Sonra küçük patch öner.
```

### 11.2 Codex İçin

Üretilecek dosyalar:

```text
AGENTS.md
.codex/config.toml
```

Codex rolü:

```text
- Büyük sprint işleri
- Repo audit
- Release readiness kontrolü
- Build/test/lint çalıştırma
- Büyük refactor planı
- README/portfolio iyileştirme
```

Codex genel kuralı:

```text
AGENTS.md kurallarına uy.
ATLAS knowledge-base içindeki proje özetini önce oku.
Gereksiz dosya okuma.
Önce yapılacak planı çıkar.
Kod değişikliği gerekiyorsa küçük ve geri alınabilir patch yap.
Değişiklik sonrası build/test/lint komutlarını önce preview et.
Onay olmadan riskli terminal komutu çalıştırma.
```

### 11.3 GitHub Copilot İçin

Üretilecek dosyalar:

```text
.github/copilot-instructions.md
.github/instructions/*.instructions.md
```

Copilot rolü:

```text
- Inline autocomplete
- Küçük fonksiyon tamamlama
- Boilerplate azaltma
- Test iskeleti önerme
- PR açıklaması yazma
- Küçük kod review yardımı
```

Copilot’a verilmemesi gereken işler:

```text
- Sınırsız terminal yetkisi
- Production deploy
- Force push
- Gizli dosya okuma
- Geniş çaplı otomatik refactor
```

---

## 12. NotebookLM Kullanım Modeli

NotebookLM, ATLAS’ın runtime beyni olmayacaktır.

Doğru kullanım:

```text
NotebookLM büyük dokümanları, PDF’leri, sprint notlarını ve proje raporlarını özetler.
Bu özetler manuel olarak E:\ATLAS\workspace\notebooklm-exports altına koyulur.
ATLAS CLI bu özetleri knowledge-base dosyalarına aktarır.
```

Örnek import:

```powershell
python -m app.cli notebooklm import AtlasPilot --source E:\ATLAS\workspace\notebooklm-exports\AtlasPilot-summary.md
```

Oluşturulacak/güncellenecek dosyalar:

```text
E:\ATLAS\workspace\knowledge-base\AtlasPilot
├── 00-project-summary.md
├── 01-architecture-map.md
├── 02-feature-index.md
├── 03-current-status.md
├── 04-risk-list.md
├── 05-release-checklist.md
├── 06-next-sprints.md
└── 07-notebooklm-import-log.md
```

---

## 13. AtlasPilot Pilot Proje Kuralları

AtlasPilot, ATLAS V1 için pilot proje olmalıdır.

Root:

```powershell
D:\AtlasPilot\android-app
```

Özel kısıtlar:

```text
- INTERNET permission eklenmeyecek.
- Cloud SDK eklenmeyecek.
- AI SDK eklenmeyecek.
- Health Connect eklenmeyecek.
- SQLCipher eklenmeyecek.
- fallbackToDestructiveMigration geri getirilmeyecek.
- Room migration düzeni bozulmayacak.
- Local-first scope korunacak.
- Turkish UI copy korunacak.
- Product source koduna sadece ilgili sprint açıkça istiyorsa dokunulacak.
```

Komutlar:

```powershell
cd D:\AtlasPilot\android-app
.\gradlew.bat assembleDebug
.\gradlew.bat testDebugUnitTest
.\gradlew.bat lint
```

ATLAS bu komutları V1’de öncelikle preview etmelidir:

```powershell
python -m app.cli command preview AtlasPilot --type build
python -m app.cli command preview AtlasPilot --type test
python -m app.cli command preview AtlasPilot --type lint
```

---

## 14. V1 / V2 / V3 Kapsam Ayrımı

## 14.1 V1 — Kontrollü Altyapı

V1’in hedefi:

```text
ATLAS güvenli, test edilebilir, local-first bir AI developer assistant altyapısıdır.
```

V1 kapsamı:

```text
- Klasör yapısı
- Python CLI core
- Config sistemi
- Safety policy
- MCP config generator
- Project registry
- Instruction template generator
- NotebookLM import
- SQLite memory
- Context manager
- Safe terminal preview
- Audit log
- Repo onboarding
- MCP install helper
- AtlasPilot pilot onboarding
- AtlasPilot knowledge-base import
- Project memory MCP
- Safe terminal MCP
- Integration check
- Report generator
- Full doctor
- V1 release candidate audit
```

V1’de yapılmayacaklar:

```text
- Tam otomatik kod yazan agent
- Sınırsız terminal
- Git push automation
- Production deploy
- Full disk access
- Secret file reading
- NotebookLM API bağımlılığı
- Copilot Cloud’a write/terminal yetkisi
```

## 14.2 V2 — Agent Intelligence

V2 kapsamı:

```text
- MainAgent
- PlannerAgent
- CodeReviewerAgent
- ProjectManagerAgent
- ResearchAgent
- MemoryAgent
- Model router
- OpenAI API / local Ollama opsiyonu
- RAG/vector index
- Tool approval UI
- Daha gelişmiş project intelligence
```

V2’ye geçiş şartları:

```text
- V1 doctor --full başarılı olmalı.
- AtlasPilot pilot onboarding başarılı olmalı.
- Instruction generation doğru çalışmalı.
- Context manager token kontrollü kaynak seçebilmeli.
- Safe command preview riskli komutları engelleyebilmeli.
- Audit log sistemi çalışmalı.
```

## 14.3 V3 — Desktop Product

V3 kapsamı:

```text
- Desktop UI
- Tauri veya Electron arayüzü
- Chat panel
- Project selector
- Tool approval ekranı
- Token usage panel
- Report browser
- Voice input/output opsiyonel
```

---

# 15. Sprint Sistemi

Aşağıdaki sprint sistemi, projeyi küçük, test edilebilir ve güvenli kalite kapılarına böler.

## Sprint 0 — Klasör Yapısı

### Amaç

`E:\ATLAS` altında güvenli, düzenli ve genişletilebilir ana klasör yapısını oluşturmak.

### Kapsam

Yapılacaklar:

```text
- Root klasör yapısı
- Alt klasörler
- İlk README dosyaları
- İlk .gitignore
- Config placeholder dosyaları
```

Yapılmayacaklar:

```text
- Python business logic
- MCP server çalıştırma
- Terminal executor
- AtlasPilot reposuna yazma
- LLM API entegrasyonu
```

### Oluşturulacak Dosyalar

```text
E:\ATLAS\README.md
E:\ATLAS\.gitignore
E:\ATLAS\assistant-core\README.md
E:\ATLAS\workspace\README.md
E:\ATLAS\configs\assistant.settings.json
E:\ATLAS\configs\safety-policy.json
E:\ATLAS\configs\mcp.master.json
E:\ATLAS\configs\project-registry.json
E:\ATLAS\templates\README.md
E:\ATLAS\logs\README.md
E:\ATLAS\backups\README.md
```

### CLI Komutları

```powershell
New-Item -ItemType Directory -Force -Path E:\ATLAS
New-Item -ItemType Directory -Force -Path E:\ATLAS\assistant-core
New-Item -ItemType Directory -Force -Path E:\ATLAS\workspace
New-Item -ItemType Directory -Force -Path E:\ATLAS\mcp-servers
New-Item -ItemType Directory -Force -Path E:\ATLAS\configs
New-Item -ItemType Directory -Force -Path E:\ATLAS\templates
New-Item -ItemType Directory -Force -Path E:\ATLAS\logs
New-Item -ItemType Directory -Force -Path E:\ATLAS\backups
```

### Güvenlik Kuralları

```text
- C:\Users açılmayacak.
- .env oluşturulmayacak.
- Private key dosyalarına erişilmeyecek.
- AtlasPilot source koduna dokunulmayacak.
- Remove-Item -Recurse kullanılmayacak.
```

### Acceptance Criteria

```text
- E:\ATLAS var.
- Tüm ana klasörler var.
- Placeholder config dosyaları var.
- README proje amacını açıklıyor.
- .gitignore hassas dosyaları dışlıyor.
```

### Test Planı

```powershell
Test-Path E:\ATLAS
Test-Path E:\ATLAS\assistant-core
Test-Path E:\ATLAS\workspace
Test-Path E:\ATLAS\configs
Test-Path E:\ATLAS\templates
Test-Path E:\ATLAS\logs
Test-Path E:\ATLAS\backups
```

### Cursor/Codex Promptu

```text
E:\ATLAS altında sadece Sprint 0 klasör yapısını oluştur.
Kod yazma.
MCP server çalıştırma.
AtlasPilot reposuna dokunma.
Placeholder README ve config dosyalarını oluştur.
Güvenlik dışı path açma.
```

### Riskler

```text
- Klasör yapısının gereğinden fazla şişmesi
- Config dosyalarında gerçek secret eklenmesi
- Yanlışlıkla farklı path’e dosya oluşturulması
```

### Sonraki Sprint Bağımlılığı

Sprint 1 Python CLI core, Sprint 0’da oluşturulan klasör yapısına bağlıdır.

---

## Sprint 1 — Python CLI Core

### Amaç

Typer + Rich tabanlı temel CLI uygulamasını kurmak.

### Kapsam

```text
- Python package yapısı
- app.cli entrypoint
- doctor temel komutu
- paths komutu
- versiyon bilgisi
```

### Dosyalar

```text
E:\ATLAS\assistant-core\pyproject.toml
E:\ATLAS\assistant-core\app\__init__.py
E:\ATLAS\assistant-core\app\cli.py
E:\ATLAS\assistant-core\app\commands\doctor.py
E:\ATLAS\assistant-core\app\commands\paths.py
E:\ATLAS\assistant-core\tests\test_cli_smoke.py
```

### CLI Komutları

```powershell
cd E:\ATLAS\assistant-core
python -m app.cli doctor
python -m app.cli paths
python -m pytest
```

### Güvenlik Kuralları

```text
- CLI hiçbir terminal komutunu çalıştırmayacak.
- Sadece path ve environment bilgisi gösterecek.
- Secret okumayacak.
```

### Acceptance Criteria

```text
- python -m app.cli doctor çalışıyor.
- python -m app.cli paths çalışıyor.
- pytest smoke test geçiyor.
```

### Riskler

```text
- CLI komutları erken karmaşıklaşabilir.
- Pathler hardcode dağınık yazılabilir.
```

---

## Sprint 2 — Config Sistemi

### Amaç

ATLAS configlerini Pydantic ile doğrulayan merkezi config loader oluşturmak.

### Kapsam

```text
- assistant.settings.json doğrulama
- project-registry.json temel doğrulama
- mcp.master.json temel doğrulama
- config validate komutu
```

### Dosyalar

```text
assistant-core\app\config\models.py
assistant-core\app\config\loader.py
assistant-core\app\commands\config.py
configs\assistant.settings.json
configs\project-registry.json
configs\mcp.master.json
```

### CLI Komutları

```powershell
python -m app.cli config validate
```

### Acceptance Criteria

```text
- Geçerli JSON dosyaları doğrulanır.
- Eksik alanlarda anlaşılır hata verir.
- Config pathleri E:\ATLAS dışına taşmaz.
```

### Riskler

```text
- JSON schema gevşek kalabilir.
- Windows path escape hataları çıkabilir.
```

---

## Sprint 3 — Safety Policy

### Amaç

Path, dosya ve komut güvenlik kurallarını merkezi policy dosyasından okumak.

### Kapsam

```text
- blocked_paths
- blocked_file_patterns
- blocked_commands
- approval_required_commands
- safety show komutu
```

### Dosyalar

```text
assistant-core\app\safety\policy.py
assistant-core\app\safety\path_guard.py
assistant-core\app\safety\command_guard.py
assistant-core\app\commands\safety.py
configs\safety-policy.json
```

### CLI Komutları

```powershell
python -m app.cli safety show
python -m app.cli command check AtlasPilot --cmd ".\gradlew.bat assembleDebug"
```

### Acceptance Criteria

```text
- Riskli pathler reddedilir.
- Riskli komutlar reddedilir.
- Approval gerektiren komutlar işaretlenir.
```

### Riskler

```text
- Komut engelleme string match ile zayıf kalabilir.
- PowerShell varyasyonları kaçabilir.
```

---

## Sprint 4 — Audit Log Temel Sistemi

### Amaç

Önemli işlemleri JSONL olarak loglayan temel audit sistemi kurmak.

### Kapsam

```text
- log writer
- tool-calls log
- errors log
- sessions log
- logs list/show komutları
```

### Dosyalar

```text
assistant-core\app\logging\audit.py
assistant-core\app\commands\logs.py
logs\tool-calls
logs\errors
logs\sessions
```

### CLI Komutları

```powershell
python -m app.cli logs list
python -m app.cli logs show --last 10
```

### Acceptance Criteria

```text
- JSONL log yazılabiliyor.
- Log dosyaları okunabiliyor.
- Sensitive content loglanmıyor.
```

### Riskler

```text
- Log içine secret düşmesi
- Log formatının ileride değişmesi
```

---

## Sprint 5 — MCP Config Generator

### Amaç

Tek `mcp.master.json` dosyasından Cursor, VS Code/Copilot ve Codex formatları üretmek.

### Kapsam

```text
- mcp list
- mcp generate
- mcp generate --target cursor
- mcp generate --target vscode
- mcp generate --target codex
```

### Dosyalar

```text
assistant-core\app\mcp\models.py
assistant-core\app\mcp\generator.py
assistant-core\app\commands\mcp.py
configs\generated\cursor.mcp.json
configs\generated\vscode.mcp.json
configs\generated\codex.config.toml
```

### Acceptance Criteria

```text
- workspace-filesystem sadece E:\ATLAS\workspace açar.
- Tüm disk açılmaz.
- Generated configler valid formatta oluşur.
```

### Riskler

```text
- MCP formatları tool versiyonlarına göre değişebilir.
- Yanlış path full disk riskine yol açabilir.
```

---

## Sprint 6 — Project Registry

### Amaç

Projeleri merkezi registry içine eklemek, listelemek, göstermek ve doğrulamak.

### Kapsam

```text
- project add
- project list
- project show
- project validate
```

### Dosyalar

```text
assistant-core\app\projects\models.py
assistant-core\app\projects\registry.py
assistant-core\app\commands\project.py
configs\project-registry.json
```

### CLI Komutları

```powershell
python -m app.cli project add --name AtlasPilot --type android-compose-room --root D:\AtlasPilot\android-app
python -m app.cli project list
python -m app.cli project show AtlasPilot
python -m app.cli project validate AtlasPilot
```

### Acceptance Criteria

```text
- Proje adı unique olur.
- Root path doğrulanır.
- Build/test/lint komutları registry’de tutulur.
- Forbidden changes kaydedilir.
```

### Riskler

```text
- Yanlış root path kaydı
- Registry ile SQLite memory arasında ileride tutarsızlık
```

---

## Sprint 7 — Instruction Templates

### Amaç

Repo bazlı AGENTS.md, Cursor rules, Copilot instructions ve Codex config üretmek.

### Kapsam

```text
- Jinja2 template sistemi
- instructions preview
- instructions generate
- instructions check
```

### Dosyalar

```text
assistant-core\app\instructions\generator.py
assistant-core\app\commands\instructions.py
templates\AGENTS.md.j2
templates\copilot-instructions.md.j2
templates\cursor-project-context.mdc.j2
templates\codex-config.toml.j2
```

### CLI Komutları

```powershell
python -m app.cli instructions preview AtlasPilot
python -m app.cli instructions generate AtlasPilot
python -m app.cli instructions check AtlasPilot
```

### Acceptance Criteria

```text
- Preview gerçek dosyaya yazmadan çıktı gösterir.
- Generate sadece beklenen repo dosyalarını üretir.
- Existing dosyalar için backup veya diff yaklaşımı vardır.
```

### Riskler

```text
- Repo içine yanlış dosya yazılması
- Tool instructionlarının fazla genel kalması
```

---

## Sprint 8 — SQLite Memory

### Amaç

Projeler, kararlar, tool calls ve raporlar için lokal SQLite memory kurmak.

### Kapsam

```text
- memory init
- memory sync-projects
- memory project-status
- memory add-decision
- memory list-decisions
```

### Dosyalar

```text
assistant-core\app\memory\db.py
assistant-core\app\memory\models.py
assistant-core\app\memory\repository.py
assistant-core\app\commands\memory.py
workspace\memory\assistant.db
```

### CLI Komutları

```powershell
python -m app.cli memory init
python -m app.cli memory sync-projects
python -m app.cli memory project-status AtlasPilot
python -m app.cli memory add-decision AtlasPilot --title "Local-first scope" --body "No cloud backend in MVP"
python -m app.cli memory list-decisions AtlasPilot
```

### Acceptance Criteria

```text
- DB oluşur.
- Registry projeleri DB’ye sync olur.
- Kararlar eklenebilir/listelenebilir.
```

### Riskler

```text
- DB migration stratejisi unutulabilir.
- JSON registry ve DB arasında source-of-truth karışabilir.
```

---

## Sprint 9 — NotebookLM Import

### Amaç

NotebookLM özetlerini proje knowledge-base dosyalarına dönüştürmek.

### Kapsam

```text
- notebooklm import
- notebooklm list
- notebooklm validate
- 00–07 knowledge-base dosyaları
```

### CLI Komutları

```powershell
python -m app.cli notebooklm import AtlasPilot --source E:\ATLAS\workspace\notebooklm-exports\AtlasPilot-summary.md
python -m app.cli notebooklm list
python -m app.cli notebooklm validate AtlasPilot
```

### Acceptance Criteria

```text
- Import edilen dosya knowledge-base’e bölünür.
- Import log tutulur.
- NotebookLM runtime bağımlılığı yoktur.
```

### Riskler

```text
- Özetlerin yanlış kategorilere bölünmesi
- NotebookLM çıktısına aşırı güvenilmesi
```

---

## Sprint 10 — Context Manager

### Amaç

Görev tipine göre token budget ve kaynak okuma planı üretmek.

### Kapsam

```text
- task type
- token budget
- source priority
- context build
- context show-plan
```

### CLI Komutları

```powershell
python -m app.cli context build AtlasPilot --task project_status
python -m app.cli context build AtlasPilot --task sprint_plan
python -m app.cli context show-plan AtlasPilot --task code_review
```

### Acceptance Criteria

```text
- simple_question tüm projeyi okumaz.
- code_review daha geniş kaynak planı çıkarır.
- large_audit yüksek budget kullanır ama kontrollü kalır.
```

### Riskler

```text
- Context manager sembolik kalabilir.
- Gerçek dosyaya inme kuralları netleşmeyebilir.
```

---

## Sprint 11 — Safe Terminal Preview

### Amaç

Registry’de tanımlı build/test/lint/status komutlarını güvenli şekilde preview etmek.

### Kapsam

```text
- command check
- command preview
- blocked command detection
- approval required detection
```

### CLI Komutları

```powershell
python -m app.cli command check AtlasPilot --cmd ".\gradlew.bat assembleDebug"
python -m app.cli command preview AtlasPilot --type build
python -m app.cli command preview AtlasPilot --type lint
python -m app.cli command preview AtlasPilot --type test
```

### Acceptance Criteria

```text
- Riskli komutlar engellenir.
- Gradle komutları approval required olarak işaretlenir.
- Preview komutu gerçek çalıştırma yapmaz.
```

### Riskler

```text
- Kullanıcı preview ile run arasındaki farkı karıştırabilir.
- Komut parsing eksik kalabilir.
```

---

## Sprint 12 — Repo Onboarding

### Amaç

Tek komutla yeni projeyi registry, knowledge-base ve instruction sistemine dahil etmek.

### CLI Komutları

```powershell
python -m app.cli onboard D:\AtlasPilot\android-app --name AtlasPilot --type android-compose-room --dry-run
python -m app.cli onboard D:\AtlasPilot\android-app --name AtlasPilot --type android-compose-room
```

### Acceptance Criteria

```text
- Dry-run gerçek dosya yazmaz.
- Onboard registry kaydı oluşturur.
- Knowledge-base klasörü oluşturur.
- Instruction dosyaları üretilebilir hale gelir.
```

### Riskler

```text
- Repo içine izinsiz yazma
- Mevcut dosyaların üzerine yazma
```

---

## Sprint 13 — MCP Install Helper

### Amaç

Generated MCP configlerini Cursor, Codex ve VS Code için kurulum önizlemesiyle hazırlamak.

### CLI Komutları

```powershell
python -m app.cli mcp install --target cursor --dry-run
python -m app.cli mcp install --target codex --dry-run
python -m app.cli mcp install --target vscode --project AtlasPilot --dry-run
```

### Acceptance Criteria

```text
- Dry-run config destination gösterir.
- Mevcut kullanıcı configleri overwrite edilmez.
- Backup planı gösterilir.
```

### Riskler

```text
- Kullanıcı config dosyalarının bozulması
- Tool-specific format uyuşmazlığı
```

---

## Sprint 14 — AtlasPilot Pilot Onboarding

### Amaç

ATLAS’ın gerçek pilot proje olarak AtlasPilot’u doğru tanımasını sağlamak.

### Kapsam

```text
- Registry kaydı
- Forbidden changes
- Build/test/lint komutları
- Instruction preview
- Integration check başlangıcı
```

### Acceptance Criteria

```text
- AtlasPilot project show doğru bilgi verir.
- AtlasPilot project validate geçer.
- Forbidden changes instructionlara yansır.
```

### Riskler

```text
- AtlasPilot source koduna gereksiz müdahale
- Local-first kısıtların unutulması
```

---

## Sprint 15 — AtlasPilot Knowledge-Base

### Amaç

AtlasPilot için 00–06 knowledge-base dosyalarını oluşturmak.

### Dosyalar

```text
workspace\knowledge-base\AtlasPilot\00-project-summary.md
workspace\knowledge-base\AtlasPilot\01-architecture-map.md
workspace\knowledge-base\AtlasPilot\02-feature-index.md
workspace\knowledge-base\AtlasPilot\03-current-status.md
workspace\knowledge-base\AtlasPilot\04-risk-list.md
workspace\knowledge-base\AtlasPilot\05-release-checklist.md
workspace\knowledge-base\AtlasPilot\06-next-sprints.md
```

### Acceptance Criteria

```text
- AtlasPilot status knowledge-base’te doğru görünür.
- Release checklist mevcut RC durumunu yansıtır.
- Next sprints gerçekçi ve local-first uyumludur.
```

### Riskler

```text
- Knowledge-base’in güncel olmaması
- NotebookLM özetinin yanlış yorumlanması
```

---

## Sprint 16 — Project-Memory MCP

### Amaç

Project registry, knowledge-base ve SQLite memory için read-only MCP server oluşturmak.

### Kapsam

```text
- read_project_registry
- read_project_summary
- read_project_status
- list_decisions
- list_reports
```

### Acceptance Criteria

```text
- MCP read-only çalışır.
- Source code değiştirme yetkisi yoktur.
- Terminal komutu çalıştırmaz.
```

### Riskler

```text
- Yanlışlıkla write yetkisi verilmesi
- Path sınırının gevşek kalması
```

---

## Sprint 17 — Safe-Terminal MCP

### Amaç

Registry’de tanımlı komutları approval token ile güvenli şekilde çalıştırabilecek MCP katmanı hazırlamak.

### Kapsam

V1’de mümkünse sadece preview + check ile başlanmalı. Gerçek run opsiyonel ve sıkı kontrollü olmalı.

### Acceptance Criteria

```text
- approval_token olmadan run yok.
- Blocked commands engellenir.
- Sadece registry command type çalışır.
- Tool call log tutulur.
```

### Riskler

```text
- Terminal yetkisinin erken açılması
- Komut enjeksiyonu
- Yanlış working directory
```

---

## Sprint 18 — Integrations Check

### Amaç

AtlasPilot ve diğer projelerde Cursor/Codex/Copilot entegrasyon dosyalarının varlığını ve tutarlılığını kontrol etmek.

### CLI Komutları

```powershell
python -m app.cli integrations check AtlasPilot
```

### Acceptance Criteria

```text
- AGENTS.md var mı?
- .cursor/rules dosyaları var mı?
- .github/copilot-instructions.md var mı?
- .codex/config.toml var mı?
- Forbidden changes yansımış mı?
```

### Riskler

```text
- Tool davranışlarının garanti edilememesi
- Sadece dosya varlığı kontrolünün yeterli sanılması
```

---

## Sprint 19 — Report Generator

### Amaç

Proje review, release audit, sprint plan ve integration check raporları üretmek.

### Rapor Tipleri

```text
project-review
release-audit
sprint-plan
code-review
integration-check
notebooklm-import
mcp-status
system-health
```

### CLI Komutları

```powershell
python -m app.cli report create AtlasPilot --type integration-check
python -m app.cli report list AtlasPilot
python -m app.cli report latest AtlasPilot
```

### Acceptance Criteria

```text
- Rapor workspace\outputs altına yazılır.
- Rapor DB’ye kaydedilir.
- Rapor tipi ve timestamp görünür.
```

### Riskler

```text
- Raporların yüzeysel kalması
- Rapor çıktılarının standardize olmaması
```

---

## Sprint 20 — Full Doctor

### Amaç

ATLAS sistem sağlığını uçtan uca kontrol etmek.

### Kontroller

```text
- Python version
- Node version
- npm version
- Git version
- Docker var mı?
- E:\ATLAS klasörleri var mı?
- Config JSON geçerli mi?
- MCP master config geçerli mi?
- Generated configler var mı?
- Project registry geçerli mi?
- SQLite DB var mı?
- Knowledge-base klasörleri var mı?
- Instruction dosyaları var mı?
- Safety policy aktif mi?
- Logs yazılabiliyor mu?
```

### CLI Komutları

```powershell
python -m app.cli doctor
python -m app.cli doctor --full
```

### Acceptance Criteria

```text
- doctor temel kontrolü hızlı çalışır.
- doctor --full tüm sistemi kontrol eder.
- Eksikler tablo halinde gösterilir.
```

### Riskler

```text
- Doctor çıktısı çok uzun olabilir.
- Bazı dependency eksikleri yanlış hata gibi algılanabilir.
```

---

## Sprint 21 — Multi-Project Rollout

### Amaç

ATLAS’ı AtlasPilot dışında diğer proje tiplerine hazırlamak.

### Desteklenecek Tipler

```text
android-compose-room
android-compose-notes
mlops-python
spring-boot
unity-game
plain-java
```

### Acceptance Criteria

```text
- Her proje tipi için temel instruction template var.
- Registry project type doğrular.
- Context manager proje tipine göre kaynak önceliği seçer.
```

### Riskler

```text
- Template karmaşası
- Her proje tipinin aynı kurallarla yönetilmeye çalışılması
```

---

## Sprint 22 — V1 Release Candidate Audit

### Amaç

ATLAS V1’in release candidate seviyesine gelip gelmediğini doğrulamak.

### Kontrol Başlıkları

```text
- CLI komutları çalışıyor mu?
- Config validate geçiyor mu?
- Safety policy aktif mi?
- MCP config generator doğru mu?
- Project registry doğru mu?
- Instruction generator doğru mu?
- NotebookLM import çalışıyor mu?
- SQLite memory çalışıyor mu?
- Context manager token-aware mı?
- Safe terminal preview çalışıyor mu?
- Audit logs yazılıyor mu?
- AtlasPilot pilot başarılı mı?
- Report generator çıktı üretiyor mu?
- doctor --full geçiyor mu?
```

### Acceptance Criteria

```text
- V1 RC raporu oluşturulur.
- Kritik riskler listelenir.
- V2’ye geçiş için hazır/koşullu hazır/no-go kararı verilir.
```

### Riskler

```text
- Eksik testlerle V1 tamamlandı sanılması
- MCP güvenlik kontrollerinin yeterince test edilmemesi
```

---

## Sprint 23 — V2 Agent Orchestrator Hazırlığı

### Amaç

V2’de gelecek agent sisteminin interface ve sınırlarını tasarlamak.

### Kapsam

```text
- Agent interface tasarımı
- Tool approval interface tasarımı
- Model router tasarımı
- MemoryAgent tasarımı
- PlannerAgent tasarımı
```

### V1’de Yapılmayacak

```text
- Tam otomatik kod yazma
- Otomatik patch uygulama
- Otomatik terminal run
- Otomatik git push
```

### Acceptance Criteria

```text
- V2 tasarım dokümanı çıkar.
- Agent yetki sınırları netleşir.
- V1 güvenlik modeli bozulmaz.
```

### Riskler

```text
- V2’ye erken kod yazılması
- Agent sisteminin güvenlik modelini delmesi
```

---

# 16. CLI Komut Haritası

V1 boyunca hedeflenen komutlar:

```powershell
python -m app.cli doctor
python -m app.cli doctor --full
python -m app.cli paths
python -m app.cli config validate
python -m app.cli safety show

python -m app.cli mcp list
python -m app.cli mcp generate
python -m app.cli mcp generate --target cursor
python -m app.cli mcp generate --target codex
python -m app.cli mcp generate --target vscode
python -m app.cli mcp install --target cursor --dry-run
python -m app.cli mcp install --target codex --dry-run
python -m app.cli mcp install --target vscode --project AtlasPilot --dry-run

python -m app.cli project add --name AtlasPilot --type android-compose-room --root D:\AtlasPilot\android-app
python -m app.cli project list
python -m app.cli project show AtlasPilot
python -m app.cli project validate AtlasPilot

python -m app.cli instructions preview AtlasPilot
python -m app.cli instructions generate AtlasPilot
python -m app.cli instructions check AtlasPilot

python -m app.cli notebooklm import AtlasPilot --source E:\ATLAS\workspace\notebooklm-exports\AtlasPilot-summary.md
python -m app.cli notebooklm list
python -m app.cli notebooklm validate AtlasPilot

python -m app.cli memory init
python -m app.cli memory sync-projects
python -m app.cli memory project-status AtlasPilot
python -m app.cli memory add-decision AtlasPilot --title "Local-first scope" --body "No cloud backend in MVP"
python -m app.cli memory list-decisions AtlasPilot

python -m app.cli context build AtlasPilot --task project_status
python -m app.cli context build AtlasPilot --task sprint_plan
python -m app.cli context show-plan AtlasPilot --task code_review

python -m app.cli command check AtlasPilot --cmd ".\gradlew.bat assembleDebug"
python -m app.cli command preview AtlasPilot --type build
python -m app.cli command preview AtlasPilot --type lint
python -m app.cli command preview AtlasPilot --type test

python -m app.cli logs list
python -m app.cli logs show --last 10
python -m app.cli logs project AtlasPilot

python -m app.cli onboard D:\AtlasPilot\android-app --name AtlasPilot --type android-compose-room --dry-run
python -m app.cli onboard D:\AtlasPilot\android-app --name AtlasPilot --type android-compose-room

python -m app.cli integrations check AtlasPilot
python -m app.cli report create AtlasPilot --type integration-check
python -m app.cli report list AtlasPilot
python -m app.cli report latest AtlasPilot
```

---

# 17. Eksik veya Çelişkili Noktalar

## 17.1 Copilot Memory Beklentisi

Copilot’un lokal SQLite memory’yi doğrudan okuması garanti değildir. Bu yüzden Copilot için en güvenilir kanal repo içindeki instruction dosyalarıdır.

Öneri:

```text
Copilot = generated instructions + repo context
Cursor/Codex = generated instructions + MCP opsiyonu
ATLAS = central memory source of truth
```

## 17.2 Safe Terminal Run Zamanlaması

V1’de gerçek terminal run açmak riskli olabilir. Önce preview/check sistemi tamamen oturmalı.

Öneri:

```text
Sprint 11: sadece preview
Sprint 17: MCP üzerinde approval-token kontrollü run opsiyonel
```

## 17.3 Registry ve SQLite Source-of-Truth

Hem JSON registry hem SQLite memory olacağı için çelişki riski vardır.

Öneri:

```text
project-registry.json = canonical project config
SQLite = runtime memory, decisions, reports, status cache
```

## 17.4 NotebookLM Import Formatı

NotebookLM çıktıları her zaman aynı yapıda olmayabilir.

Öneri:

```text
İlk V1 import basit section parser olsun.
Belirsiz bölümleri inbox/review alanına atsın.
Otomatik kesin karar vermesin.
```

## 17.5 MCP Path Güvenliği

Filesystem MCP yalnızca `E:\ATLAS\workspace` açmalı. Proje source rootları doğrudan MCP’ye açılmamalı.

Öneri:

```text
Source code erişimi V1’de CLI/repo instruction üretimi ile sınırlı kalsın.
MCP workspace alanı knowledge-base ve outputs odaklı olsun.
```

## 17.6 V2 Agent Sınırları

V2’de agent sistemi gelince güvenlik modeli bozulmamalı.

Öneri:

```text
Agent karar verir ama tool çalıştırmaz.
Tool çağrısı approval katmanından geçer.
```

---

# 18. Genel Risk Matrisi

| Risk | Seviye | Açıklama | Önlem |
|---|---:|---|---|
| Scope creep | Yüksek | V1’e agent, RAG, desktop UI sıkıştırılabilir | V1/V2/V3 sınırları korunmalı |
| MCP full disk access | Kritik | Yanlış filesystem config tüm diski açabilir | Sadece `E:\ATLAS\workspace` |
| Secret leakage | Kritik | `.env`, key, keystore okunabilir/loglanabilir | blocked patterns + log sanitizer |
| Terminal command injection | Yüksek | Kullanıcı girdisi komuta karışabilir | whitelist + registry command type |
| Registry/SQLite çelişkisi | Orta | İki kaynak farklı veri tutabilir | JSON config canonical, SQLite memory |
| Tool-specific format değişimi | Orta | Cursor/Codex/Copilot configleri değişebilir | generator modüler yazılmalı |
| Over-token usage | Orta | Büyük proje komple okunabilir | context manager read plan |
| AtlasPilot scope bozulması | Yüksek | INTERNET/AI/Cloud eklenebilir | forbidden_changes instructionlara basılmalı |
| Log şişmesi | Düşük/Orta | JSONL büyür | rotation/cleanup V2 |
| NotebookLM’e aşırı güven | Orta | Özet hatalı olabilir | import log + review alanı |

---

# 19. V1 Kalite Kapıları

V1 bitti demek için şu kalite kapıları geçmeli:

```text
1. python -m app.cli doctor başarılı
2. python -m app.cli doctor --full başarılı veya açıklamalı uyarılarla tamamlanıyor
3. config validate başarılı
4. safety show beklenen kuralları gösteriyor
5. mcp generate Cursor/VSCode/Codex configlerini üretiyor
6. project add/list/show/validate çalışıyor
7. instructions preview/generate/check çalışıyor
8. notebooklm import knowledge-base dosyalarını üretiyor
9. memory init/sync/decision komutları çalışıyor
10. context build summary-first plan üretiyor
11. command preview gerçek run yapmadan komutu gösteriyor
12. blocked command check riskli komutları engelliyor
13. logs list/show çalışıyor
14. onboard dry-run güvenli çalışıyor
15. AtlasPilot pilot doğru kısıtlarla onboard ediliyor
16. integrations check dosya varlığını ve kural yansımasını kontrol ediyor
17. report create çıktı üretiyor
18. V1 RC audit raporu oluşuyor
```

---

# 20. AtlasPilot İçin Örnek Knowledge-Base Başlıkları

## `00-project-summary.md`

```md
# AtlasPilot — Project Summary

- Project type: android-compose-room
- Root: D:\AtlasPilot\android-app
- Scope: local-first, manual-first personal wellness/form tracking app
- Current stage: Portfolio-ready MVP / conditional RC
- No internet/cloud/AI/Health Connect/SQLCipher in MVP
```

## `01-architecture-map.md`

```md
# Architecture Map

- UI: Jetpack Compose
- DI: Hilt
- Persistence: Room
- Architecture: repository + use case + ViewModel
- Data ownership: local export/import
```

## `02-feature-index.md`

```md
# Feature Index

- Daily form
- Water quick add
- History
- Weekly summary
- Settings
- Onboarding
- Export/data ownership
- Migration hardening
```

## `03-current-status.md`

```md
# Current Status

- Build: successful
- Lint: successful with warnings
- Unit tests: successful
- Release APK: unsigned
- Portfolio readiness: strong
- Play Store readiness: not yet
```

## `04-risk-list.md`

```md
# Risk List

- Production package name still needed for Play Store
- Signing/AAB needed
- Privacy policy needed
- Store assets/screenshots needed
- Connected instrumented test evidence needed
```

## `05-release-checklist.md`

```md
# Release Checklist

## Portfolio
- README updated
- Known limitations documented
- Screenshots added or pending

## Play Store
- Package rename
- Signing config
- AAB
- Privacy policy
- Data Safety
- Store assets
```

## `06-next-sprints.md`

```md
# Next Sprints

- Release Candidate QA checkpoint
- Screenshots and portfolio polish
- Play Store preparation
- Privacy/security V2 planning
```

---

# 21. Sprint 0 Uygulama Planı — Net Versiyon

## Amaç

`E:\ATLAS` altında ATLAS’ın tüm ana klasörlerini ve başlangıç dokümantasyonunu oluşturmak.

## Yapılacaklar

```text
1. Root klasörü oluştur.
2. assistant-core alt yapısını oluştur.
3. workspace alt yapısını oluştur.
4. mcp-servers alt yapısını oluştur.
5. configs alt yapısını oluştur.
6. templates alt yapısını oluştur.
7. logs alt yapısını oluştur.
8. backups alt yapısını oluştur.
9. README.md oluştur.
10. .gitignore oluştur.
11. Placeholder config dosyalarını oluştur.
```

## PowerShell Klasör Komutları

```powershell
New-Item -ItemType Directory -Force -Path E:\ATLAS

New-Item -ItemType Directory -Force -Path E:\ATLAS\assistant-core\app
New-Item -ItemType Directory -Force -Path E:\ATLAS\assistant-core\agents
New-Item -ItemType Directory -Force -Path E:\ATLAS\assistant-core\context
New-Item -ItemType Directory -Force -Path E:\ATLAS\assistant-core\memory
New-Item -ItemType Directory -Force -Path E:\ATLAS\assistant-core\safety
New-Item -ItemType Directory -Force -Path E:\ATLAS\assistant-core\tools
New-Item -ItemType Directory -Force -Path E:\ATLAS\assistant-core\prompts
New-Item -ItemType Directory -Force -Path E:\ATLAS\assistant-core\tests

New-Item -ItemType Directory -Force -Path E:\ATLAS\workspace\projects
New-Item -ItemType Directory -Force -Path E:\ATLAS\workspace\knowledge-base
New-Item -ItemType Directory -Force -Path E:\ATLAS\workspace\notebooklm-exports
New-Item -ItemType Directory -Force -Path E:\ATLAS\workspace\raw-sources
New-Item -ItemType Directory -Force -Path E:\ATLAS\workspace\memory
New-Item -ItemType Directory -Force -Path E:\ATLAS\workspace\outputs
New-Item -ItemType Directory -Force -Path E:\ATLAS\workspace\inbox
New-Item -ItemType Directory -Force -Path E:\ATLAS\workspace\vector-index

New-Item -ItemType Directory -Force -Path E:\ATLAS\mcp-servers\project-memory-mcp
New-Item -ItemType Directory -Force -Path E:\ATLAS\mcp-servers\safe-terminal-mcp
New-Item -ItemType Directory -Force -Path E:\ATLAS\mcp-servers\docs-index-mcp

New-Item -ItemType Directory -Force -Path E:\ATLAS\configs\generated

New-Item -ItemType Directory -Force -Path E:\ATLAS\templates

New-Item -ItemType Directory -Force -Path E:\ATLAS\logs\tool-calls
New-Item -ItemType Directory -Force -Path E:\ATLAS\logs\approvals
New-Item -ItemType Directory -Force -Path E:\ATLAS\logs\errors
New-Item -ItemType Directory -Force -Path E:\ATLAS\logs\sessions

New-Item -ItemType Directory -Force -Path E:\ATLAS\backups\memory-backups
New-Item -ItemType Directory -Force -Path E:\ATLAS\backups\knowledge-base-backups
New-Item -ItemType Directory -Force -Path E:\ATLAS\backups\config-backups
New-Item -ItemType Directory -Force -Path E:\ATLAS\backups\repo-file-backups
```

## Sprint 0 Sonunda Kontrol

```powershell
Test-Path E:\ATLAS
Test-Path E:\ATLAS\assistant-core\app
Test-Path E:\ATLAS\workspace\knowledge-base
Test-Path E:\ATLAS\configs\generated
Test-Path E:\ATLAS\logs\tool-calls
Test-Path E:\ATLAS\backups\config-backups
```

## Sprint 0 Başarı Kriteri

```text
ATLAS henüz kod çalıştıran bir sistem değildir.
Fakat güvenli root yapısı, config alanı, workspace alanı, log alanı ve backup alanı hazırdır.
Sprint 1’de Python CLI core yazılabilecek hale gelmiştir.
```

---

# 22. Sonuç ve Ana Tavsiye

Bu proje gerçekten güçlü bir portföy/kişisel üretkenlik altyapısı projesi olabilir. Ama başarı için en önemli konu scope’u doğru sıraya koymaktır.

En doğru strateji:

```text
Önce güvenli merkez → sonra proje registry → sonra instruction üretimi → sonra context manager → sonra safe preview → sonra MCP → en son agent
```

Yani V1’in başarı cümlesi şu olmalı:

```text
ATLAS, projelerimi güvenli şekilde kaydediyor, knowledge-base oluşturuyor, AI araçlarına ortak instruction üretiyor, token kontrollü context planı çıkarıyor, riskli komutları engelliyor ve her şeyi logluyor.
```

V1 bu seviyeye gelirse, V2’de gerçek agent orchestrator eklemek çok daha güvenli ve sürdürülebilir olur.

