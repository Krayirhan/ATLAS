# ATLAS - Current status

- **Release:** **V1 RC - GO**
- **Root:** `E:\ATLAS` canonical. `D:\ATLAS` operational root degildir.
- **Pilot / self-project:** **ATLAS**. **BenimFormum** bu sprint kapsaminda degil.
- **Sprint 28:** Read-only Ollama AI layer tamamlandi.
- **Sprint 28.6:** Warm-up, keep-alive, timeout ve context visibility hardening tamamlandi.
- **Sprint 29:** `MemoryAgent` ve `ProjectQAAgent` tamamlandi.
- **Sprint 30:** `PlannerAgent` tamamlandi.
- **Sprint 31:** `CodeReviewerAgent` tamamlandi.
- **Sprint 32:** `ToolApprovalAgent` ve preview-only approval workflow tamamlandi.
- **Sprint 33:** `MainAgent` tamamlandi.
- **Sprint 34:** `SecurityAuditorAgent` tamamlandi:
  - `python -m app.cli ai security-audit --project ATLAS --scope all-light`
  - agent capability / MCP / approval / context / docs bounded audit
- **AI guvenlik siniri:** dosya yazan AI yok, terminal run yok, MCP tool call yok, git action yok, prompt tam loglama yok.
- **Context kaynaklari:** registry + memory status + secili KB dosyalari + latest report metadata. Tum repo taranmiyor.
- **Doctor / audit:** `doctor --full`, `ai doctor`, `audit v1-rc` ana saglik sinyalleridir.
