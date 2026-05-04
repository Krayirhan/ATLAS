# NotebookLM Workflow

## Critical distinctions

- **NotebookLM is not a runtime dependency of ATLAS.** ATLAS runs without Google NotebookLM online or any NotebookLM API.
- **NotebookLM is not the “brain” of ATLAS.** Authoritative state lives in **registry**, **SQLite memory**, **knowledge-base markdown**, and **reports** under `E:\ATLAS`.
- **NotebookLM API integration** is **not** part of V1 / early V2 baseline: ingestion is **manual export → file → CLI import**.

## Correct usage (happy path)

1. Large PDFs, sprint notes, architecture drafts, or long reports are uploaded to **NotebookLM manually** (user’s Google workflow).
2. User generates a **structured summary** in NotebookLM (outline, bullets, tables as appropriate).
3. User saves the summary as **Markdown** under:

   `E:\ATLAS\workspace\notebooklm-exports`

   Prefer the `_templates` in that folder to keep sections consistent.

4. ATLAS imports the file into the project knowledge flow:

   ```text
   python -m app.cli notebooklm import ATLAS --source E:\ATLAS\workspace\notebooklm-exports\<file>.md
   ```

5. Import updates or supplements **knowledge-base** material (per existing CLI behavior and templates).
6. Future **AI context loader** reads knowledge-base files (and other allowed sources per `11-ai-context-contract.md`) — not NotebookLM directly.

## Folder layout (target)

```text
E:\ATLAS\workspace\notebooklm-exports
├── README.md
├── _templates
│   ├── atlas-notebooklm-export-template.md
│   ├── project-summary-export-template.md
│   ├── sprint-report-export-template.md
│   └── risk-audit-export-template.md
└── incoming-exports   (isteğe bağlı; ham/ara özet dosyaları buraya konabilir)
```

## Summary formats to request from NotebookLM

When prompting NotebookLM (human-side), ask for sections aligned with ATLAS KB:

- Project summary  
- Architecture map  
- Feature index  
- Current status  
- Risk list  
- Release checklist  
- Next sprints  
- Decisions  
- Open questions  

## Related CLI (existing)

```text
python -m app.cli notebooklm list
python -m app.cli notebooklm import ATLAS --source E:\ATLAS\workspace\notebooklm-exports\<file>.md
python -m app.cli notebooklm validate ATLAS
```

## Policy

- Do **not** place secrets, API keys, or private keys in exports.
- Do **not** treat exports as executable code.
