# V2 Agent Orchestrator — Tasarım Özeti (Sprint 23)

Bu doküman V1 güvenlik modelini **bozmadan** V2’de planlanan agent katmanının sınırlarını netleştirir. **Uygulama kodu V2’ye ertelenir**; burada yalnızca arayüz ve yetki sınırları tanımlanır.

## 1. Hedef

- Merkezi planlama ve görev dağılımı (orchestrator)
- Araç çağrılarında **onay katmanı** ve denetlenebilirlik
- Model seçimi (router) ile maliyet/latency kontrolü

## 2. V1’den miras (değişmeyecek ilkeler)

- **Önce oku → planla → önizle → onay → uygula/logla**
- Registry + safety policy + audit log tek doğruluk kaynağı
- Secret ve riskli path okuma yok
- Otomatik `git push`, production deploy, sınırsız terminal **yok**

## 3. Bileşenler (mantıksal)

| Bileşen | Rol | V1’de |
|--------|-----|--------|
| **Orchestrator API** | Görev alır, alt agentlara **salt okunur** bağlam verir | Yok |
| **PlannerAgent** | Adım listesi ve risk notları üretir; **dosya yazmaz** | Yok |
| **MemoryAgent** | SQLite / knowledge özeti okur; **tek yazma**: onaylı memory güncellemeleri | Kısmen CLI |
| **CodeReviewerAgent** | Diff / statik öneri; **patch uygulamaz** (V2 erken faz) | Yok |
| **Model router** | Görev tipine göre model / token limiti | Context manager ile hizalı |
| **Tool approval** | Terminal / MCP run öncesi kullanıcı veya token onayı | safe-terminal MCP |

## 4. Arayüzler (soyut)

- `AgentContext`: proje adı, görev tipi, token bütçesi, policy referansı
- `AgentPlan`: adımlar, `requires_approval` bayrakları, tahmini risk
- `ToolInvocation`: hedef (ör. safe-terminal `run`), payload, approval id
- `OrchestratorResult`: plan, ara çıktılar, log referansları (secret yok)

## 5. V1’de yapılmayacaklar (Sprint 23 teyidi)

- Tam otomatik kod yazma ve patch uygulama
- Onaysız terminal çalıştırma
- Otomatik `git push` / merge

## 6. V2’ye geçiş önkoşulları (hatırlatma)

- `doctor --full` temiz veya yalnızca kabul edilebilir uyarılar
- `audit v1-rc` **GO** veya açık gerekçeli **CONDITIONAL**
- MCP üretimi ve safe-terminal onay akışı sahada doğrulanmış olmalı

## 7. Sonuç

V2 orchestrator, **karar üretir ve planı denetlenebilir şekilde yayınlar**; yürütme her zaman mevcut ATLAS güvenlik ve onay katmanlarından geçer.
